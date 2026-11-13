"""Render a stick-figure sword fight to MP4.

python3 fights/render.py OUT.mp4 [--fight power|patience] [--wide] [--scale 0.5]
                                 [--stills DIR --still-times 1.0,2.5]
"""
import argparse
import importlib
import math
import os
import subprocess
import sys
import tempfile
import wave

import numpy as np
import skia

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import audio  # noqa: E402
import elements  # noqa: E402
import powers  # noqa: E402
from draw import col, draw_fighter, draw_spear_head, fill, stroke, polyline  # noqa: E402
from rig import R_HEAD, solve  # noqa: E402

FPS = 60
FONT_DIR = "/usr/share/fonts/opentype/inter/"
FIGHTS = {"spear": "choreo_spear", "patience": "choreo", "power": "choreo_power", "fire": "choreo_fire", "time": "choreo_time"}


def typeface(weight="ExtraBold"):
    path = os.path.join(FONT_DIR, f"Inter-{weight}.otf")
    if os.path.exists(path):
        return skia.Typeface.MakeFromFile(path)
    return skia.Typeface("DejaVu Sans", skia.FontStyle.Bold())


# ------------------------------------------------------------ time map
def build_timemap(ev, end):
    stops = sorted((t, kw["dur"]) for t, k, kw in ev if k == "hitstop")
    slows = [(kw["a0"], kw["a1"], kw["rate"]) for t, k, kw in ev if k == "slowmo"]
    frames = []
    t = 0.0
    si = 0
    while t <= end:
        frames.append(t)
        rate = 1.0
        for a0, a1, r in slows:
            if a0 <= t < a1:
                rate = r
        nt = t + rate / FPS
        while si < len(stops) and stops[si][0] < t:
            si += 1
        if si < len(stops) and nt >= stops[si][0]:
            h, dur = stops[si]
            frames.append(h)
            frames.extend([h] * max(0, int(round(dur * FPS)) - 1))
            si += 1
            t = h + rate / FPS * 0.5
            continue
        t = nt
    return np.array(frames)


def video_time(frames, ta):
    idx = np.searchsorted(frames, ta - 1e-9)
    return min(idx, len(frames) - 1) / FPS


def clamp_chain(pts, seg):
    """Keep a rope's segments at most seg long (stops tails stretching)."""
    out = [pts[0]]
    for q in pts[1:]:
        px, py = out[-1]
        dx, dy = q[0] - px, q[1] - py
        L = math.hypot(dx, dy)
        if L > seg:
            dx, dy = dx / L * seg, dy / L * seg
        out.append((px + dx, py + dy))
    return out


def seg_closest(p1, q1, p2, q2):
    """Midpoint of the closest points between two segments."""
    p1, q1, p2, q2 = map(np.array, (p1, q1, p2, q2))
    d1, d2, r = q1 - p1, q2 - p2, p1 - p2
    a, e, f = d1 @ d1, d2 @ d2, d2 @ r
    c = d1 @ r
    b = d1 @ d2
    den = a * e - b * b
    s = np.clip((b * f - c * e) / den, 0, 1) if den > 1e-9 else 0.0
    t = np.clip((b * s + f) / e, 0, 1)
    s = np.clip((b * t - c) / a, 0, 1)
    c1, c2 = p1 + d1 * s, p2 + d2 * t
    return tuple((c1 + c2) / 2)


class Fight:
    def __init__(self, name):
        mod = importlib.import_module(FIGHTS[name])
        d = mod.build()
        self.fighters = d["fighters"]       # [(id, track, style)], draw order
        self.ev = d["events"]
        self.end = d["end"]
        self.title = d["title"]
        self.hp = d.get("hp", [])
        self.theme = d.get("theme", "day")
        self.springy = d.get("springy", False)
        self.tracks = {i: (tr, st) for i, tr, st in self.fighters}
        self.ids = [i for i, _, _ in self.fighters]
        self.smooth = {}
        if d.get("springy"):
            imp = {i: [] for i in self.ids}
            for t, k, kw in self.ev:
                v = kw.get("v", 1.0) * (1.6 if kw.get("big") else 1.0)
                if k in ("hit", "dmg"):
                    on = kw.get("on") or kw.get("who") or self.other(kw["by"])
                    imp[on].append((t, dict(T=-650 * v, H=-1500 * v, uab=-900 * v,
                                            fab=-1200 * v)))
                elif k == "clash":
                    for i in self.ids:
                        imp[i].append((t, dict(T=-260 * v, H=-700 * v, sw=-500 * v,
                                               uab=-500 * v)))
                elif k == "flinch":
                    imp[kw["who"]].append((t, dict(T=-500 * v, H=-1200 * v)))
            import motion
            for i, tr, st in self.fighters:
                self.smooth[i] = motion.Smoothed(tr, self.end, imp[i], st.get("springs"))

    def joints(self, who, t):
        tr, st = self.tracks[who]
        p, x = (self.smooth[who] if who in self.smooth else tr).sample(t)
        return solve(p, x, tr.facing(t), size=st.get("size", 1.0),
                     blade=st.get("blade", 72), grip_off=st.get("grip_off", 9.0),
                     butt=st.get("butt", 8.0))

    def other(self, who):
        return [i for i in self.ids if i != who][0]


# ------------------------------------------------------------ renderer
class Renderer:
    def __init__(self, fight="power", wide=False, scale=1.0):
        self.wide = wide
        self.W, self.H = (1920, 1080) if wide else (1080, 1920)
        self.W, self.H = int(self.W * scale), int(self.H * scale)
        self.s = scale
        self.gy = self.H * (0.80 if wide else 0.62)
        self.f = Fight(fight)
        self.frames = build_timemap(self.f.ev, self.f.end)
        self.n = len(self.frames)
        self.font_big = skia.Font(typeface("ExtraBold"), 96 * scale)
        self.font_mid = skia.Font(typeface("ExtraBold"), 64 * scale)
        self.font_small = skia.Font(typeface("Bold"), 30 * scale)
        self.prepare_events()
        self.prepare_camera()

    # ---------------------------------------------------- events
    def prepare_events(self):
        f = self.f
        self.fx = []
        self.cues = []
        self.iai_vt = None
        self.slow_vt = None
        self.focus = []
        self.win = None
        self.breaks = []
        self.blood = []      # (vt, pt, dir, n, seed)
        self.wounds = {}     # who -> [(vt, u, ang, len)]
        self.damage = []     # (vt, who, amt)
        self.craters = []    # (vt, x, size, seed)
        self.decaps = []     # (t, who, J_victim, J_attacker)
        self.banners = []    # (vt, text)
        self.hp = f.hp
        self.el = []         # elemental effects (elements.py)
        self.el_marks = {}
        powers.init(self)
        for t, k, kw in f.ev:
            vt = video_time(self.frames, t)
            seed = len(self.fx)
            if elements.prepare(self, t, vt, k, kw) or powers.prepare(self, t, vt, k, kw):
                continue
            if k == "clash":
                a, b = f.joints(f.ids[0], t), f.joints(f.ids[1], t)
                pt = seg_closest(a["w0"], a["tip"], b["w0"], b["tip"])
                self.fx.append((vt, k, dict(kw, pt=pt, seed=seed)))
            elif k == "hit":
                A = f.joints(kw["by"], t)
                if kw.get("part"):
                    pt = A[kw["part"]]
                else:
                    B = f.joints(kw["on"], t)
                    pt = seg_closest(A["guard"], A["tip"], B["hip"], B["neck"])
                self.fx.append((vt, k, dict(kw, pt=pt, seed=seed)))
                on = kw.get("on") or f.other(kw["by"])
                B = f.joints(on, t)
                dirx = 1.0 if B["hip"][0] > A["hip"][0] else -1.0
                self.add_wound(vt, on, B, pt, seed)
                self.blood.append((vt, pt, dirx, 16 if kw.get("big") else 11, seed))
                self.damage.append((vt, on, kw.get("dmg", 0)))
            elif k == "decap":
                self.decaps.append((t, kw["who"], f.joints(kw["who"], t),
                                    f.joints(kw["by"], t)))
                self.fx.append((vt, "decap", dict(kw, seed=seed, big=True)))
                # head bounce sounds, in sync with the head physics below
                J, A = f.joints(kw["who"], t), f.joints(kw["by"], t)
                R = R_HEAD * J["size"]
                y, vy = J["head"][1], 420.0
                tt, n = 0.0, 0
                while tt < 3 and n < 3:
                    vy -= 1500 / 240
                    y += vy / 240
                    if y <= R and vy < 0:
                        y = R
                        if abs(vy) * 0.35 >= 60:
                            self.cues.append((video_time(self.frames, t + tt), "thud",
                                              dict(v=0.5 / (n + 1))))
                        vy = -vy * 0.35
                        n += 1
                    tt += 1 / 240
            elif k == "dmg":
                A, B = f.joints(kw["by"], t), f.joints(kw["who"], t)
                pt = ((B["hip"][0] * 0.4 + B["neck"][0] * 0.6),
                      (B["hip"][1] * 0.4 + B["neck"][1] * 0.6))
                dirx = 1.0 if B["hip"][0] > A["hip"][0] else -1.0
                self.add_wound(vt, kw["who"], B, pt, seed)
                self.add_wound(vt, kw["who"], B, pt, seed + 1)
                self.blood.append((vt, pt, dirx, 34 if kw.get("big") else 22, seed))
                self.damage.append((vt, kw["who"], kw["amt"]))
            elif k == "slam":
                A = f.joints(kw["by"], t)
                self.fx.append((vt, k, dict(kw, pt=(A["tip"][0], 2.0), seed=seed)))
                self.craters.append((vt, A["tip"][0], 1.0, seed))
            elif k in ("ground", "dust", "skid", "gust", "stomp"):
                self.fx.append((vt, k, dict(kw, pt=(kw["x"], 2.0), seed=seed)))
            elif k == "scrape":
                self.fx.append((vt, k, dict(kw, t0=t, seed=seed)))
                kw = dict(kw, vdur=video_time(self.frames, t + kw["dur"]) - vt)
            elif k == "radial":
                self.fx.append((vt, k, dict(kw, seed=seed)))
            elif k == "iai":
                self.iai_vt, self.iai_t = vt, t
                self.fx.append((vt, "iai", kw))
            elif k == "slowmo":
                self.slow_vt = (video_time(self.frames, kw["a0"]),
                                video_time(self.frames, kw["a1"]))
                self.cues.append((self.slow_vt[0], "riser",
                                  dict(dur=self.slow_vt[1] - self.slow_vt[0] + 0.1)))
            elif k == "break":
                self.breaks.append((t, kw["who"], f.joints(kw["who"], t)))
            elif k == "winner":
                self.win = (vt, kw["name"], kw.get("color", "#d8323c"))
            elif k == "banner":
                self.banners.append((vt, kw["text"]))
            elif k == "focus":
                end = kw.get("until")
                self.focus.append((vt, video_time(self.frames, end) if end else 1e9,
                                   kw["who"]))
            elif k in ("twinkle", "charge"):
                self.fx.append((vt, k, dict(kw, seed=seed)))
                if k == "charge":
                    self.cues.append((vt, "riser", dict(dur=kw["dur"])))
            if "stop_at" in kw:
                kw = dict(kw, vstop=video_time(self.frames, kw["stop_at"]))
            self.cues.append((vt, k, kw))
        self.stop_ranges = []
        for t, k, kw in f.ev:
            if k != "hitstop":
                continue
            whos, m = set(), 3.0
            for t2, k2, kw2 in f.ev:
                if abs(t2 - t) < 0.02:
                    if k2 in ("hit", "dmg"):
                        whos.add(kw2.get("on") or kw2.get("who") or f.other(kw2["by"]))
                        m = max(m, 7.0 if kw2.get("big") else 5.0)
                    elif k2 == "clash":
                        whos.update(f.ids)
                        m = max(m, 5.0 if kw2.get("big") else 3.0)
            a = video_time(self.frames, t)
            self.stop_ranges.append((a, a + kw["dur"], whos, m))
        powers.finish(self)
        self.auto_swooshes()

    def add_wound(self, vt, who, B, pt, seed):
        hx, hy = B["hip"]
        nx, ny = B["neck"]
        vx, vy = nx - hx, ny - hy
        L2 = vx * vx + vy * vy
        u = ((pt[0] - hx) * vx + (pt[1] - hy) * vy) / max(1e-6, L2)
        u = min(0.9, max(0.15, u))
        rng = np.random.default_rng(seed + 5)
        self.wounds.setdefault(who, []).append(
            (vt, u, rng.uniform(-0.9, 0.9), rng.uniform(10, 16)))

    def hp_at(self, who, vt, lag=0.0):
        hp = 100.0
        for et, w, amt in self.damage:
            if w == who and et + lag <= vt:
                hp -= amt
        return max(0.0, hp)

    def auto_swooshes(self):
        f = self.f
        skip = [self.iai_t] if self.iai_vt is not None else []
        twirls = [(t0 - 0.1, t0 + kw.get("dur", 0.15) + 0.1) for t0, k, kw in f.ev if k in ("twirl", "thrust")]
        for who in f.ids:
            st = f.tracks[who][1]
            if st.get("unarmed"):
                continue
            heavy = st.get("sword") == "cleaver"
            spear = st.get("sword") == "spear"
            last = -9
            dt = 1 / 240
            t = 0.0
            prev = None
            while t < f.end:
                J = f.joints(who, t)
                tip = J["tip"]
                if prev is not None and J["p"]["sheath"] < 0.5:
                    sp = math.hypot(tip[0] - prev[0], tip[1] - prev[1]) / dt
                    gap = 0.3 if heavy else 0.09
                    if sp > 1600 and t - last > gap and \
                            all(abs(t - s) > 0.2 for s in skip) and \
                            not (spear and any(a <= t <= b for a, b in twirls)):
                        self.cues.append((video_time(self.frames, t), "swoosh",
                                          dict(v=min(1.0, 0.5 + sp / 6000),
                                               heavy=heavy, spear=spear)))
                        last = t
                prev = tip
                t += dt

    # ---------------------------------------------------- camera
    def prepare_camera(self):
        f = self.f
        cams = []
        cx = z = None
        for i, t in enumerate(self.frames):
            vt = i / FPS
            Js = [f.joints(w, t) for w in f.ids]
            xs = [J["hip"][0] for J in Js]
            for t0, who, J0, A0 in self.decaps:
                if t >= t0:   # keep the flying head in the shot
                    d_ = 1 if J0["hip"][0] > A0["hip"][0] else -1
                    xs.append(J0["hip"][0] + d_ * 170)
            foc = [w for a, b, w in self.focus if a <= vt < b]
            if foc:
                J = f.joints(foc[0], t)
                mid, dist = J["hip"][0], 160
            else:
                mid, dist = (min(xs) + max(xs)) / 2, max(xs) - min(xs)
            if self.wide:
                tz = min(self.W / (dist + 700), 2.8 * self.s)
            elif f.springy:
                tz = min(self.W / (dist + 190), 2.9 * self.s)
            else:
                tz = min(self.W / (dist + 260), 3.2 * self.s)
            if self.slow_vt and self.slow_vt[0] <= vt <= self.slow_vt[1] + 0.05:
                u = (vt - self.slow_vt[0]) / (self.slow_vt[1] - self.slow_vt[0])
                tz *= 1 + 0.25 * min(1, u)
            if cx is None:
                cx, z = mid, tz
            cx += (mid - cx) * 0.10
            z += (tz - z) * (0.10 if tz < z else 0.05)
            if self.iai_vt is not None and 0 <= vt - self.iai_vt < 0.2:
                cx, z = mid, tz
            cams.append((cx, z))
        self.cams = cams

    def tilt(self, vt):
        if not self.f.springy:
            return 0.0
        a = 0.0
        for et, k, d in self.fx:
            dt = vt - et
            if 0 <= dt < 1.2 and (d.get("big") or k == "slam"):
                a += 2.2 * d.get("v", 1.0) * math.exp(-dt * 4.5) * math.cos(dt * 18 + d.get("seed", 0))
        return max(-3.0, min(3.0, a))

    def radial(self, c, pt, flat, i):
        """Anime impact frame: speed lines bursting out of the hit point."""
        rng = np.random.default_rng(i * 7 + 3)
        px, py = pt
        for k in range(46):
            ang = rng.uniform(0, 2 * math.pi)
            r0 = rng.uniform(70, 160)
            r1 = r0 + rng.uniform(300, 1100)
            w = rng.uniform(2, 9)
            p_ = skia.Path()
            ca, sa = math.cos(ang), math.sin(ang)
            p_.moveTo(px + ca * r0, py + sa * r0)
            p_.lineTo(px + ca * r1 - sa * w, py + sa * r1 + ca * w)
            p_.lineTo(px + ca * r1 + sa * w, py + sa * r1 - ca * w)
            p_.close()
            c.drawPath(p_, fill(col(flat or "#ffffff", 0.9)))

    def shake_punch(self, vt):
        sx = sy = punch = 0.0
        if powers.stopped_vt(self, vt):
            return sx, sy, punch
        for et, k, d in self.fx:
            dt = powers.wdt(self, vt, et)
            if dt < 0 or dt > 1.0:
                continue
            m = {"clash": 8, "hit": 4, "slam": 34, "stomp": 7, "iai": 16, "boom": 22}.get(k, 0)
            m *= d.get("v", 1.0) * (2.0 if d.get("big") else 1.0)
            if m == 0:
                continue
            e = math.exp(-dt * (6 if k == "slam" else 9))
            sx += m * e * math.sin(dt * 87 + d.get("seed", 0))
            sy += m * e * math.cos(dt * 71 + 1.3 * d.get("seed", 0))
            if k in ("slam", "iai") or d.get("big"):
                punch += 0.12 * math.exp(-dt * 6)
            elif self.f.springy and k in ("hit", "clash"):
                punch += 0.05 * math.exp(-dt * 9)
        return sx * self.s, sy * self.s, punch

    # ---------------------------------------------------- background
    def background_night(self, c, cx, z, dark):
        """Moonlit courtyard: deep blue sky, stars, big pale moon, dark hills."""
        W, H, gy, s = self.W, self.H, self.gy, self.s
        sky = skia.Paint()
        sky.setShader(skia.GradientShader.MakeLinear(
            [(0, 0), (0, gy)], [col("#09090b").toColor(), col("#25242a").toColor()]))
        c.drawRect(skia.Rect(0, 0, W, gy), sky)
        rng = np.random.default_rng(4)
        for i in range(90):
            x = (rng.uniform(0, W * 1.3) - cx * 0.03 * s) % W
            y = rng.uniform(0, gy * 0.9)
            c.drawCircle(x, y, rng.uniform(0.8, 2.4) * s, fill(col("#ffffff", rng.uniform(0.3, 0.9))))
        mx = W * 0.62 - cx * 0.06 * s
        my = gy - (0.34 if self.wide else 0.25) * H
        R = 0.24 * min(W, H)
        c.drawCircle(mx, my, R * 1.5, fill(col("#d9d6cc", 0.07)))
        c.drawCircle(mx, my, R * 1.2, fill(col("#e6e2d6", 0.09)))
        c.drawCircle(mx, my, R, fill(col("#f4efd8")))
        c.drawCircle(mx - R * 0.3, my - R * 0.2, R * 0.16, fill(col("#e2dcc0", 0.7)))
        c.drawCircle(mx + R * 0.25, my + R * 0.3, R * 0.22, fill(col("#e2dcc0", 0.6)))
        for layer, (par, amp, color) in enumerate(((0.12, 2.3, "#1b1a1f"), (0.25, 1.4, "#121115"))):
            path = skia.Path()
            path.moveTo(0, gy)
            for i in range(0, W + 20, 20):
                wx = (i - W / 2) / (par * z) + cx * par + layer * 900
                h = 46 + 28 * math.sin(wx * 0.004) + 16 * math.sin(wx * 0.011 + 1) \
                    + 8 * math.sin(wx * 0.031)
                path.lineTo(i, gy - h * s * amp)
            path.lineTo(W, gy)
            path.close()
            c.drawPath(path, fill(col(color)))
        fl = skia.Paint()
        fl.setShader(skia.GradientShader.MakeLinear(
            [(0, gy), (0, H)], [col("#2b2a30").toColor(), col("#131216").toColor()]))
        c.drawRect(skia.Rect(0, gy, W, H), fl)
        lp = stroke(col("#66646e", 0.45), 2 * s)
        step = 140
        k0 = int((cx - W / z) // step) - 2
        for k in range(k0, k0 + int(2 * W / z / step) + 6):
            sx = W / 2 + (k * step - cx) * z
            c.drawLine(sx, gy, W / 2 + (sx - W / 2) * 3.2, H, lp)
        for j in range(1, 6):
            yy = gy + (H - gy) * (j / 6) ** 1.6
            c.drawLine(0, yy, W, yy, stroke(col("#66646e", 0.3), 1.5 * s))
        c.drawLine(0, gy, W, gy, stroke(col("#dcdae0"), 3.5 * s))
        if dark > 0:
            c.drawRect(skia.Rect(0, 0, W, H), fill(col("#050410", dark)))

    def background(self, c, cx, z, dark):
        if self.f.theme == "night":
            return self.background_night(c, cx, z, dark)
        W, H, gy = self.W, self.H, self.gy
        sky = skia.Paint()
        sky.setShader(skia.GradientShader.MakeLinear(
            [(0, 0), (0, gy)], [col("#eadfcb").toColor(), col("#f7f2e9").toColor()]))
        c.drawRect(skia.Rect(0, 0, W, gy), sky)
        sxp = W / 2 - cx * 0.08 * self.s
        c.drawCircle(sxp, gy - (0.30 if self.wide else 0.22) * H, 0.30 * min(W, H),
                     fill(col("#e6a48f", 0.42)))
        path = skia.Path()
        path.moveTo(0, gy)
        for i in range(0, W + 20, 20):
            wx = (i - W / 2) / (0.25 * z) + cx * 0.25
            h = 40 + 25 * math.sin(wx * 0.004) + 15 * math.sin(wx * 0.011 + 1) \
                + 8 * math.sin(wx * 0.031)
            path.lineTo(i, gy - h * self.s * 1.4)
        path.lineTo(W, gy)
        path.close()
        c.drawPath(path, fill(col("#d9c9b0", 0.8)))
        fl = skia.Paint()
        fl.setShader(skia.GradientShader.MakeLinear(
            [(0, gy), (0, H)], [col("#e2d5bf").toColor(), col("#cdbb9f").toColor()]))
        c.drawRect(skia.Rect(0, gy, W, H), fl)
        lp = stroke(col("#b9a585", 0.55), 2 * self.s)
        step = 140
        k0 = int((cx - W / z) // step) - 2
        for k in range(k0, k0 + int(2 * W / z / step) + 6):
            sx = W / 2 + (k * step - cx) * z
            c.drawLine(sx, gy, W / 2 + (sx - W / 2) * 3.2, H, lp)
        for j in range(1, 6):
            yy = gy + (H - gy) * (j / 6) ** 1.6
            c.drawLine(0, yy, W, yy, stroke(col("#b9a585", 0.35), 1.5 * self.s))
        c.drawLine(0, gy, W, gy, stroke(col("#2a2622"), 3.5 * self.s))
        if dark > 0:
            c.drawRect(skia.Rect(0, 0, W, H), fill(col("#120e14", dark)))

    # ---------------------------------------------------- pieces
    def tails(self, who, t):
        f = self.f
        S = f.tracks[who][1].get("size", 1.0)
        L = 10 if f.tracks[who][1].get("fast") else 7
        pts_a, pts_b = [], []
        for k in range(L):
            J = f.joints(who, t - k * 0.03)
            hx, hy = J["head"]
            fc = J["facing"]
            flut = math.sin(t * 15 + k * 0.9) * k * 1.4
            base = (hx - fc * (R_HEAD - 2) * S, hy + 3)
            pts_a.append((base[0] - fc * k * 7, base[1] - k * 1.2 + flut))
            pts_b.append((base[0] - fc * k * 6, base[1] - k * 3.2 - flut * 0.8))
        J = f.joints(who, t)
        hx, hy = J["head"]
        pts_a[0] = pts_b[0] = (hx - J["facing"] * (R_HEAD - 2) * S, hy + 3)
        if f.springy:
            pts_a, pts_b = clamp_chain(pts_a, 8 * S), clamp_chain(pts_b, 7 * S)
        return pts_a, pts_b

    def tassel(self, c, who, t, flat):
        """Red horsehair tassel under the spearhead: trails behind every move."""
        f = self.f
        st = f.tracks[who][1]
        if st.get("sword") != "spear" or not st.get("tassel"):
            return
        J = f.joints(who, t)
        if J["p"].get("broken", 0) > 0.5:
            return
        S = J["size"]
        off = 12 + st.get("blade", 72) - st.get("head_len", 26) - 3

        def anchor(tt):
            K = f.joints(who, tt)
            hx, hy = K["haf"]
            sx, sy = K["sw_dir"]
            return hx + sx * off * S * K["size"], hy + sy * off * S * K["size"]
        for strand in range(3):
            pts = []
            for k in range(8):
                ax, ay = anchor(t - k * 0.018)
                fl = math.sin(t * 19 + k * 0.8 + strand * 2.1) * k * 0.9
                pts.append((ax + fl * 0.4, ay - k * k * 0.32 - k * 1.2 + fl * 0.3 - strand * 1.5))
            pts[0] = anchor(t)
            pts = clamp_chain(pts, (4.2 + strand * 0.6) * S)
            polyline(c, pts, stroke(col(flat or st["tassel"]), (4.6 - strand) * S))

    def jitter(self, who, i):
        """Shake a fighter in place while the hit-stop holds the frame."""
        vt = i / FPS
        for a, b, whos, m in self.stop_ranges:
            if who in whos and a <= vt < b:
                u = (vt - a) / max(1e-3, b - a)
                return m * (1 - u) * (1 if i % 2 else -1), 0.0
        return 0.0, 0.0

    def blade_trail(self, c, who, t, color):
        f = self.f
        N, dt = 10, 0.012
        prev = None
        for k in range(N):
            J = f.joints(who, t - k * dt)
            if J["p"]["sheath"] > 0.5:
                break
            g, tip = J["guard"], J["tip"]
            base = (g[0] + (tip[0] - g[0]) * 0.3, g[1] + (tip[1] - g[1]) * 0.3)
            if prev is not None:
                pt, pb = prev
                if math.hypot(tip[0] - pt[0], tip[1] - pt[1]) > 3.0:
                    path = skia.Path()
                    path.moveTo(*pt)
                    path.lineTo(*tip)
                    path.lineTo(*base)
                    path.lineTo(*pb)
                    path.close()
                    c.drawPath(path, fill(col(color, 0.75 * (1 - k / N) ** 1.3)))
            prev = (tip, base)

    def ghosts(self, c, who, t, style, flat):
        f = self.f
        a, b = f.joints(who, t), f.joints(who, t - 1 / 60)
        sp = math.hypot(a["hip"][0] - b["hip"][0], a["hip"][1] - b["hip"][1]) * 60
        if sp < 600:
            return
        n = 7 if style.get("fast") else 4
        for k in range(1, n + 1):
            J = f.joints(who, t - k * 0.011)
            draw_fighter(c, J, style, alpha=0.38 * (1 - k / (n + 1)), flat=flat)

    def speed_lines(self, c, who, t, color):
        """Horizontal streaks behind a fighter moving very fast."""
        f = self.f
        a, b = f.joints(who, t), f.joints(who, t - 1 / 60)
        vx = (a["hip"][0] - b["hip"][0]) * 60
        if abs(vx) < 1500:
            return
        rng = np.random.default_rng(int(t * 1000))
        hx, hy = a["hip"]
        for i in range(9):
            y = hy + rng.uniform(-70, 90)
            ln = rng.uniform(120, 320)
            x0 = hx - np.sign(vx) * rng.uniform(20, 80)
            c.drawLine(x0, y, x0 - np.sign(vx) * ln, y,
                       stroke(col(color, 0.55), rng.uniform(1.5, 3.5)))

    def star(self, c, x, y, r, a, n, seed, color="#ffcf5a"):
        rng = np.random.default_rng(seed + 99)
        path = skia.Path()
        rot = rng.uniform(0, 1)
        for i in range(2 * n):
            rr = r if i % 2 == 0 else r * 0.28
            ang = (i / (2 * n) + rot) * 2 * math.pi
            px, py = x + math.cos(ang) * rr, y + math.sin(ang) * rr
            path.moveTo(px, py) if i == 0 else path.lineTo(px, py)
        path.close()
        c.drawPath(path, fill(col("#ffffff", a)))
        c.drawPath(path, stroke(col(color, a), 2))

    def dust(self, c, rng, px, dt, v, life=1.0, spread=1.0, color="#b9a17e"):
        for i in range(int(8 * v) + 3):
            side = -1 if i % 2 else 1
            spd = rng.uniform(40, 170) * v * spread
            x = px + side * spd * (1 - math.exp(-dt * 4)) / 1.2
            y = 12 + rng.uniform(5, 40) * dt * v
            r = (6 + 30 * v * (1 - math.exp(-dt * 5))) * rng.uniform(0.7, 1.2)
            a = 0.5 * max(0, 1 - dt / life) ** 1.5
            c.drawCircle(x, y, r, fill(col(color, a)))

    def cracks(self, c, rng, px, dt, n, reach, life):
        a = 0.9 * max(0, 1 - dt / life)
        for i in range(n):
            side = -1 if i % 2 else 1
            x, pts = px, [(px, 1)]
            for j in range(4):
                x += side * rng.uniform(0.5, 1.2) * reach / 4
                pts.append((x, 1 - rng.uniform(1, 9) * (j + 1) * 0.6))
            polyline(c, pts, stroke(col("#3a3128", a), 2.6))

    def draw_fx(self, c, vt):
        t_now = self.frames[min(self.n - 1, int(round(vt * FPS)))]
        for et, k, d in self.fx:
            if k == "scrape" and d["t0"] <= t_now <= d["t0"] + d["dur"] + 0.4:
                f = self.f
                rng = np.random.default_rng(d["seed"])
                tt = d["t0"]
                while tt < min(t_now, d["t0"] + d["dur"]):
                    a, b = f.joints(f.ids[0], tt), f.joints(f.ids[1], tt)
                    px, py = seg_closest(a["w0"], a["tip"], b["w0"], b["tip"])
                    for j in range(3):
                        age = t_now - tt
                        life = rng.uniform(0.15, 0.4)
                        ang = rng.uniform(0, 2 * math.pi)
                        sp = rng.uniform(200, 700)
                        vx, vy = math.cos(ang) * sp, math.sin(ang) * sp + 200
                        if age > life:
                            continue
                        x = px + vx * age
                        y = py + vy * age - 900 * age * age
                        c.drawLine(x, y, x - vx * 0.02, y - (vy - 1800 * age) * 0.02,
                                   stroke(col("#ffd36b", 1 - age / life), 2.4))
                    tt += 1 / 120
                if t_now <= d["t0"] + d["dur"]:
                    a, b = f.joints(f.ids[0], t_now), f.joints(f.ids[1], t_now)
                    px, py = seg_closest(a["w0"], a["tip"], b["w0"], b["tip"])
                    fl = 0.7 + 0.3 * math.sin(t_now * 90)
                    c.drawCircle(px, py, 22 * fl, fill(col("#ffd36b", 0.35)))
                    c.drawCircle(px, py, 9 * fl, fill(col("#ffffff", 0.9)))
                continue
            if k == "radial":
                continue
            dt = powers.wdt(self, vt, et)
            if dt < 0:
                continue
            rng = np.random.default_rng(d.get("seed", 0) + 11)
            px, py = d.get("pt", (0, 0))
            if k == "clash" and dt < 0.5:
                big = d.get("big", False)
                n = 30 if big else 14
                for i in range(n):
                    ang = rng.uniform(0, 2 * math.pi)
                    spd = rng.uniform(250, 900) * (1.4 if big else 1)
                    vx, vy = math.cos(ang) * spd, math.sin(ang) * spd + 150
                    life = rng.uniform(0.18, 0.45)
                    if dt > life:
                        continue
                    x = px + vx * dt
                    y = py + vy * dt - 700 * dt * dt
                    tx, ty = x - vx * 0.025, y - (vy - 1400 * dt) * 0.025
                    c.drawLine(x, y, tx, ty, stroke(col("#ffd36b", 1 - dt / life), 2.6))
                if dt < 0.14:
                    r = (34 if big else 18) + dt * (700 if big else 450)
                    self.star(c, px, py, r, 1 - dt / 0.14, 8 if big else 6, d["seed"])
                if big and dt < 0.3:
                    r = 20 + dt * 1100
                    c.drawCircle(px, py, r, stroke(col("#ffffff", 0.8 * (1 - dt / 0.3)),
                                                   6 * (1 - dt / 0.3) + 1))
            elif k == "hit" and dt < 0.3:
                # bright slash mark across the body + small sparks
                ang = rng.uniform(-0.9, 0.9) + (math.pi / 2 if rng.random() < 0.4 else 0)
                L = 55 * min(1, dt / 0.04)
                a = 1 - dt / 0.3
                ux, uy = math.cos(ang), math.sin(ang)
                c.drawLine(px - ux * L, py - uy * L, px + ux * L, py + uy * L,
                           stroke(col("#ffffff", a), 7 * a + 1))
                c.drawLine(px - ux * L, py - uy * L, px + ux * L, py + uy * L,
                           stroke(col("#7fd4ff", a), 2.5))
                for i in range(8):
                    an = rng.uniform(0, 2 * math.pi)
                    sp = rng.uniform(200, 600)
                    x = px + math.cos(an) * sp * dt
                    y = py + math.sin(an) * sp * dt - 600 * dt * dt
                    c.drawCircle(x, y, 2.5, fill(col("#fff1b8", a)))
                if d.get("big") and dt < 0.12:
                    self.star(c, px, py, 26 + dt * 400, 1 - dt / 0.12, 7, 3)
            elif k == "slam":
                v = d.get("v", 1.0)
                if dt < 0.6:   # shockwave ring along the ground
                    for side in (-1, 1):
                        r = 30 + dt * 900
                        a = 0.8 * (1 - dt / 0.6)
                        c.drawOval(skia.Rect(px - r, -8 - r * 0.06, px + r, 8 + r * 0.06),
                                   stroke(col("#fff7e6", a), 7 * (1 - dt / 0.6) + 1))
                if dt < 0.12:
                    self.star(c, px, 10, 60 + dt * 900, 1 - dt / 0.12, 9, d["seed"])
                if dt < 1.6:
                    self.dust(c, rng, px, dt, 2.2 * v, life=1.6, spread=1.6)
                if dt < 1.3:   # rocks
                    for i in range(16):
                        vx = rng.uniform(-420, 420)
                        vy = rng.uniform(300, 750)
                        x = px + vx * dt
                        y = 4 + vy * dt - 1300 * dt * dt
                        if y < 0:
                            continue
                        r = rng.uniform(3, 7)
                        c.drawRect(skia.Rect(x - r, y - r, x + r, y + r),
                                   fill(col("#5b4a39", 1 - dt / 1.3)))
                if dt < 4.0:
                    self.cracks(c, rng, px, dt, 10, 230, 4.0)
            elif k in ("dust", "ground", "skid", "gust", "stomp") and dt < 1.0:
                v = d.get("v", 1.0)
                if k == "ground":
                    self.dust(c, rng, px, dt, 1.6 * v)
                    if dt < 1.6:
                        self.cracks(c, rng, px, dt, 7, 90, 1.6)
                elif k == "stomp":
                    self.dust(c, rng, px, dt, 0.7 * v, life=0.7)
                elif k == "skid":
                    self.dust(c, rng, px, dt, 0.9 * v, life=0.8, spread=0.6)
                elif k == "gust":
                    for i in range(6):
                        y = rng.uniform(20, 140)
                        x = px + rng.uniform(-60, 60) - 600 * dt * (1 if i % 2 else 0.8)
                        a = 0.6 * (1 - dt)
                        c.drawLine(x, y, x + 120, y, stroke(col("#ffffff", a), 3))
                else:
                    self.dust(c, rng, px, dt, v)
            elif k == "charge":
                dur = d["dur"]
                if dt < dur + 0.1:
                    who = "S"
                    J = self.f.joints(who, self.frames[min(self.n - 1, int(vt * FPS))])
                    hx, hy = J["hip"]
                    for i in range(14):
                        ph = (dt * 3 + i / 14) % 1
                        ang = i * 2.4
                        r0 = 120 * (1 - ph)
                        x, y = hx + math.cos(ang) * r0, hy + math.sin(ang) * r0 * 0.8
                        c.drawLine(x, y, x + math.cos(ang) * 22, y + math.sin(ang) * 18,
                                   stroke(col("#5fc2ff", 0.8 * ph), 3))
                    c.drawCircle(hx, hy, 90 + 10 * math.sin(dt * 40),
                                 fill(col("#5fc2ff", 0.12 + 0.1 * dt / dur)))

    BLOOD = "#b5121b"

    def draw_blood(self, c, vt, flat):
        g = 1500.0
        for et, (px, py), dirx, n, seed in self.blood:
            dt = powers.wdt(self, vt, et)
            if dt < 0:
                continue
            rng = np.random.default_rng(seed + 77)
            for i in range(n):
                vx = dirx * rng.uniform(80, 520) + rng.uniform(-60, 60)
                vy = rng.uniform(-50, 420)
                r = rng.uniform(2.2, 5.0)
                # time when the drop hits the ground (y = 0)
                tl = (vy + math.sqrt(vy * vy + 2 * g * max(py, 1))) / g
                if dt < tl:
                    x = px + vx * dt
                    y = py + vy * dt - 0.5 * g * dt * dt
                    sp = math.hypot(vx, vy - g * dt)
                    stretch = min(3.0, 1 + sp / 400)
                    ang = math.atan2(vy - g * dt, vx)
                    ux, uy = math.cos(ang), math.sin(ang)
                    c.drawLine(x - ux * r * stretch, y - uy * r * stretch, x, y,
                               stroke(col(flat or self.BLOOD), r * 1.6))
                elif not flat and i % 3 == 0:
                    lx = px + vx * tl
                    grow = min(1, (dt - tl) / 0.15)
                    w = r * (1.0 + 0.8 * grow)
                    c.drawOval(skia.Rect(lx - w, -6.5, lx + w, -2.5),
                               fill(col(self.BLOOD, 0.75)))
            if dt < 0.12:   # burst at the wound
                a = 1 - dt / 0.12
                for i in range(8):
                    an = dirx * 0 + rng.uniform(-1.2, 1.2) + (0 if dirx > 0 else math.pi)
                    L = 18 + dt * 400
                    c.drawLine(px, py, px + math.cos(an) * L, py + math.sin(an) * L,
                               stroke(col(flat or self.BLOOD, a), 4 * a + 1))

    def head_piece(self, c, t, flat):
        """The cut-off head: flies, bounces, then rolls to a stop."""
        f = self.f
        for t0, who, J, A in self.decaps:
            if t < t0:
                continue
            st = f.tracks[who][1]
            S = J["size"]
            R = R_HEAD * S * st.get("head", 1.0)
            dirx = 1.0 if J["hip"][0] > A["hip"][0] else -1.0
            x, y = J["head"]
            vx, vy, ang, w = dirx * 150, 420, 0.0, dirx * -12
            dt, tt = 1 / 240, 0.0
            trail = []
            while tt < t - t0:
                vy -= 1500 * dt
                x += vx * dt
                y += vy * dt
                if y <= R and vy < 0:
                    y = R
                    vy = -vy * 0.35
                    vx *= 0.7
                    if abs(vy) < 60:
                        vy = 0
                if y <= R + 0.5 and vy == 0:
                    vx *= 0.985
                    w = -vx / R
                ang += w * dt
                tt += dt
                trail.append((x, y))
            c.drawCircle(x, y, R, fill(col(flat or st["body"])))
            if st.get("band"):
                ux, uy = math.cos(ang + math.pi / 2), math.sin(ang + math.pi / 2)
                rx, ry = math.cos(ang), math.sin(ang)
                cx, cy = x + ux * 3 * S, y + uy * 3 * S
                c.drawLine(cx - rx * R, cy - ry * R, cx + rx * R, cy + ry * R,
                           stroke(col(flat or st["band"]), 4.5 * S, skia.Paint.kButt_Cap))
                # scarf tails trailing behind the head
                tl = [(x - rx * R, y - ry * R)]
                for k in range(1, 6):
                    i = max(0, len(trail) - 1 - k * 6)
                    px_, py_ = trail[i] if trail else (x, y)
                    tl.append((px_ - rx * R - k * 2 * dirx, py_ - ry * R + 1))
                polyline(c, tl, stroke(col(flat or st["band"]), 3.4 * S))
            # cut face of the neck
            c.drawCircle(x - math.cos(ang + math.pi / 2) * R * 0.9,
                         y - math.sin(ang + math.pi / 2) * R * 0.9, R * 0.35,
                         fill(col(flat or "#7a0a10")))

    def neck_fountain(self, c, t, flat):
        f = self.f
        g = 1500.0
        for t0, who, J0, A in self.decaps:
            if t < t0:
                continue
            rng = np.random.default_rng(91)
            te = t0
            i = 0
            while te < min(t, t0 + 2.2):
                J = f.joints(who, te)
                nx, ny = J["neck"]
                hx, hy = J["hip"]
                L = math.hypot(nx - hx, ny - hy)
                ux, uy = (nx - hx) / L, (ny - hy) / L
                k = (te - t0) / 2.2
                pulse = 0.65 + 0.35 * math.sin(te * 28)
                sp = (420 * (1 - 0.75 * k) * pulse) * rng.uniform(0.8, 1.15)
                spread = rng.uniform(-0.35, 0.35)
                vx = (ux * math.cos(spread) - uy * math.sin(spread)) * sp
                vy = (ux * math.sin(spread) + uy * math.cos(spread)) * sp
                age = t - te
                r = rng.uniform(2.0, 4.2)
                tl = (vy + math.sqrt(vy * vy + 2 * g * max(ny, 1))) / g
                if age < tl:
                    x = nx + vx * age
                    y = ny + vy * age - 0.5 * g * age * age
                    a = math.atan2(vy - g * age, vx)
                    c.drawLine(x - math.cos(a) * r * 2.2, y - math.sin(a) * r * 2.2, x, y,
                               stroke(col(flat or self.BLOOD), r * 1.6))
                elif not flat and i % 5 == 0:
                    lx = nx + vx * tl
                    c.drawOval(skia.Rect(lx - r * 1.6, -6.5, lx + r * 1.6, -2.5),
                               fill(col(self.BLOOD, 0.75)))
                te += 0.022
                i += 1

    def draw_wounds(self, c, who, J, vt, flat):
        S = J["size"]
        hx, hy = J["hip"]
        nx, ny = J["neck"]
        base = math.atan2(ny - hy, nx - hx)
        for et, u, ang, ln in self.wounds.get(who, []):
            if vt < et:
                continue
            x, y = hx + (nx - hx) * u, hy + (ny - hy) * u
            a = base + math.pi / 2 + ang
            L = ln * S * 0.5 * min(1, (vt - et) / 0.05)
            ux, uy = math.cos(a), math.sin(a)
            c.drawLine(x - ux * L, y - uy * L, x + ux * L, y + uy * L,
                       stroke(col(flat or "#5a0508"), 4.2 * S))
            c.drawLine(x - ux * L * 0.8, y - uy * L * 0.8, x + ux * L * 0.8,
                       y + uy * L * 0.8, stroke(col(flat or "#ff4a4a"), 1.6 * S))
            # a drip running down
            dl = min(16, (vt - et) * 10) * S
            if dl > 1:
                c.drawLine(x, y, x + 1.0, y - dl, stroke(col(flat or self.BLOOD, 0.9), 2.2 * S))

    def draw_craters(self, c, vt, flat):
        for et, x0, size, seed in self.craters:
            if vt < et:
                continue
            rng = np.random.default_rng(seed + 31)
            u = min(1, (vt - et) / 0.08)
            w = 150 * size * u
            # broken pit cut into the floor (below the ground line)
            path = skia.Path()
            path.moveTo(x0 - w, 0)
            n = 9
            for i in range(1, n):
                xx = x0 - w + 2 * w * i / n
                depth = (22 + rng.uniform(-6, 10)) * math.sin(math.pi * i / n) * u
                path.lineTo(xx, -depth)
            path.lineTo(x0 + w, 0)
            path.close()
            c.drawPath(path, fill(col(flat or "#3b2f25", 0.95)))
            # raised slabs tilted up at the rim
            for side in (-1, 1):
                for j in range(3):
                    cxs = x0 + side * (w * 0.55 + j * 22 * size)
                    h = (14 - j * 3) * u
                    tilt = side * (8 + j * 3)
                    p2 = skia.Path()
                    p2.moveTo(cxs - 12, 0)
                    p2.lineTo(cxs - 12 + tilt * 0.3, h)
                    p2.lineTo(cxs + 12 + tilt, h * 0.7)
                    p2.lineTo(cxs + 12, 0)
                    p2.close()
                    c.drawPath(p2, fill(col(flat or "#8a7258")))
                    c.drawPath(p2, stroke(col(flat or "#3b2f25"), 2))
            # long cracks that stay
            rng2 = np.random.default_rng(seed + 32)
            for i in range(12):
                side = -1 if i % 2 else 1
                x, pts = x0 + side * w * 0.6, [(x0 + side * w * 0.6, 0)]
                for j in range(5):
                    x += side * rng2.uniform(18, 50) * u
                    pts.append((x, -rng2.uniform(0, 26) * (j + 1) * 0.35))
                polyline(c, pts, stroke(col(flat or "#3a3128", 0.85), 2.4))

    def draw_hp(self, c, vt):
        if not self.hp:
            return
        W, H, s = self.W, self.H, self.s
        top = (0.16 if not self.wide else 0.13) * H + 45 * s
        bw, bh, gap = W * 0.40, 30 * s, W * 0.05
        for i, (who, name, color) in enumerate(self.hp):
            x0 = W / 2 - gap / 2 - bw if i == 0 else W / 2 + gap / 2
            hp = self.hp_at(who, vt) / 100
            lag = self.hp_at(who, vt, lag=0.45) / 100
            # shake the bar right after taking damage
            jit = 0
            for et, w, amt in self.damage:
                if w == who and 0 <= vt - et < 0.25 and amt > 0:
                    jit = 6 * s * math.sin((vt - et) * 120) * (1 - (vt - et) / 0.25)
            x0 += jit
            c.drawRoundRect(skia.Rect(x0 - 4 * s, top - 4 * s, x0 + bw + 4 * s, top + bh + 4 * s),
                            8 * s, 8 * s, fill(col("#1b1714", 0.85)))
            c.drawRect(skia.Rect(x0, top, x0 + bw, top + bh), fill(col("#3a302a")))
            # white "damage taken" lag bar, then the real bar
            if i == 0:
                c.drawRect(skia.Rect(x0 + bw * (1 - lag), top, x0 + bw, top + bh),
                           fill(col("#fff4d6")))
                c.drawRect(skia.Rect(x0 + bw * (1 - hp), top, x0 + bw, top + bh),
                           fill(col(color)))
            else:
                c.drawRect(skia.Rect(x0, top, x0 + bw * lag, top + bh), fill(col("#fff4d6")))
                c.drawRect(skia.Rect(x0, top, x0 + bw * hp, top + bh), fill(col(color)))
            c.drawRect(skia.Rect(x0, top, x0 + bw, top + bh * 0.35),
                       fill(col("#ffffff", 0.18)))
            label = f"{int(round(hp * 100))}"
            fw = self.font_small.measureText(label)
            lx = x0 + 10 * s if i == 0 else x0 + bw - fw - 10 * s
            c.drawString(label, lx + 1.5 * s, top + bh - 4.5 * s, self.font_small,
                         fill(col("#1b1714", 0.8)))
            c.drawString(label, lx, top + bh - 6 * s, self.font_small,
                         fill(col("#ffffff")))

    def broken_pieces(self, c, t, flat):
        for bt, who, J in self.breaks:
            if t < bt:
                continue
            st = self.f.tracks[who][1]
            spear = st.get("sword") == "spear"
            g, tip = (J["haf"] if spear else J["guard"]), J["tip"]
            dx, dy = tip[0] - g[0], tip[1] - g[1]
            L = math.hypot(dx, dy)
            ux, uy = dx / L, dy / L
            cut = (st.get("cut", 34) if spear else 34) * J["size"]
            p0 = (g[0] + ux * cut, g[1] + uy * cut)
            half = (L - cut) / 2
            x, y = (p0[0] + tip[0]) / 2, (p0[1] + tip[1]) / 2
            vx, vy, a, w = -J["facing"] * 50, 60, math.atan2(uy, ux), 7.0
            dt = 1 / 240
            tt = 0
            while tt < t - bt:
                vy -= 1100 * dt
                x += vx * dt
                y += vy * dt
                a += w * dt
                if y - abs(math.sin(a)) * half <= 1.5 and vy < 0:
                    y = 1.5 + abs(math.sin(a)) * half
                    vy = -vy * 0.25
                    vx *= 0.5
                    w *= 0.4
                    if abs(vy) < 40:
                        vy = 0
                        a += (round(a / math.pi) * math.pi - a) * 0.2
                tt += dt
            ex, ey = math.cos(a) * half, math.sin(a) * half
            if spear:
                S = J["size"]
                ca, sa = math.cos(a), math.sin(a)
                hl = st.get("head_len", 26) * S
                p1 = (x + ex, y + ey)
                hb = (p1[0] - ca * hl, p1[1] - sa * hl)
                c.drawLine(x - ex, y - ey, hb[0], hb[1], stroke(col(flat or "#1d1612"), 6.4 * S))
                c.drawLine(x - ex, y - ey, hb[0], hb[1], stroke(col(flat or st.get("wood", "#8a5a33")), 3.6 * S))
                draw_spear_head(c, hb, p1, ca, sa, -sa, ca, S, st, 1.0, flat)
                continue
            c.drawLine(x - ex, y - ey, x + ex, y + ey, stroke(col(flat or "#222222"), 5.2))
            c.drawLine(x - ex, y - ey, x + ex, y + ey, stroke(col(flat or "#e9eef2"), 2.6))

    def text_center(self, c, s, y, font, color, a=1.0, x=None):
        w = font.measureText(s)
        c.drawString(s, (x if x is not None else self.W / 2) - w / 2, y, font,
                     fill(col(color, a)))

    # ---------------------------------------------------- frame
    def draw_one(self, c, who, t, vt, flat):
        f = self.f
        tr, style = f.tracks[who]
        J = f.joints(who, t)
        if not flat:
            S = J["size"]
            sa = max(0.0, 0.28 - J["hip"][1] / 900)
            c.drawOval(skia.Rect(J["hip"][0] - 34 * S, -5, J["hip"][0] + 34 * S, 5),
                       fill(col("#3a2e22", sa)))
        self.ghosts(c, who, t, style, flat or style.get("ghost", "#888888"))
        tails = self.tails(who, t) if style.get("band") else None
        draw_fighter(c, J, style, flat=flat, tails=tails)
        if not flat:
            self.draw_wounds(c, who, J, vt, flat)
        if J["p"]["sheath"] < 0.5 and not style.get("unarmed"):
            self.blade_trail(c, who, t, "#ffffff" if flat else style.get("trail", "#ffffff"))

    def render_frame(self, c, i):
        f = self.f
        t = self.frames[i]
        vt = i / FPS
        cx, z = self.cams[i]
        shx, shy, punch = self.shake_punch(vt)
        z *= 1 + punch
        W, H = self.W, self.H

        mode = "normal"
        self.impact_pt = None
        for et, k, d in self.fx:
            dtf = (vt - et) * FPS
            if (k in ("clash", "hit", "decap", "boom") and d.get("big") or k == "slam") and 0 <= dtf < 3:
                mode = "invert"
                if self.f.springy:
                    mode = "invert" if int(dtf) != 1 else "bw"
                    self.impact_pt = d.get("pt")
            if k == "iai":
                if 0 <= dtf < 3:
                    mode = "white"
                elif 3 <= dtf < 16:
                    mode = "slash"
        dark = 0.0
        if self.slow_vt and self.iai_vt and self.slow_vt[0] <= vt < self.iai_vt:
            u = (vt - self.slow_vt[0]) / max(1e-3, self.iai_vt - self.slow_vt[0])
            dark = 0.35 * min(1, u * 2)
        if self.iai_vt and 0 <= vt - self.iai_vt < 2.0 and mode == "normal":
            dark = 0.35 * max(0, 1 - (vt - self.iai_vt - 0.27) / 1.2)
        for et, k, d in self.fx:
            if k == "charge" and 0 <= vt - et < d["dur"] + 0.6:
                u = (vt - et) / d["dur"]
                dark = max(dark, 0.3 * min(1, u) * min(1, (d["dur"] + 0.6 - (vt - et)) / 0.3))

        if mode == "white":
            c.clear(col("#ffffff"))
            return
        tilt = self.tilt(vt)
        c.save()
        if tilt:
            c.translate(W / 2, H / 2)
            c.rotate(tilt)
            k_ = 1 + abs(tilt) * 0.045
            c.scale(k_, k_)
            c.translate(-W / 2, -H / 2)
        sw_who, sg, _, _ = powers.stop_state(self, t)
        if sg > 0:
            c.saveLayer(None, powers.gray_paint(sg, cold=self.f.theme == "night"))
        if mode in ("invert", "slash"):
            c.clear(col("#0d0b10"))
        elif mode == "bw":
            c.clear(col("#f4f1ea"))
        else:
            self.background(c, cx, z, dark)

        flat = "#f4f1ea" if mode in ("invert", "slash") else ("#0d0b10" if mode == "bw" else None)
        c.save()
        c.translate(W / 2 - cx * z + shx, self.gy + shy)
        c.scale(z, -z)
        if self.impact_pt is not None:
            self.radial(c, self.impact_pt, flat, i)
        if not flat:
            for who in f.ids:
                J = f.joints(who, t)
                if J["p"].get("hidden") or (sg > 0 and who == sw_who):
                    continue
                S = J["size"]
                h = J["hip"][1]
                sa = max(0.0, 0.28 - h / 900)
                c.drawOval(skia.Rect(J["hip"][0] - 34 * S, -5, J["hip"][0] + 34 * S, 5),
                           fill(col("#3a2e22", sa)))
        self.draw_craters(c, vt, flat)
        elements.draw_ground(self, c, t, flat)
        elements.draw_back(self, c, t, flat)
        powers.draw_world(self, c, t, vt, flat)
        for who in f.ids:
            tr, style = f.tracks[who]
            if f.joints(who, t)["p"].get("hidden") or (sg > 0 and who == sw_who):
                continue
            if not flat and style.get("fast"):
                self.speed_lines(c, who, t, style["ghost"])
            jx, jy = self.jitter(who, i)
            c.save()
            c.translate(jx, jy)
            self.ghosts(c, who, t, style, flat or style.get("ghost", "#888888"))
            J = f.joints(who, t)
            tails = self.tails(who, t) if style.get("band") else None
            self.tassel(c, who, t, flat)
            draw_fighter(c, J, style, flat=flat, tails=tails)
            elements.decorate(self, c, who, J, style, t, flat)
            if not flat:
                self.draw_wounds(c, who, J, vt, flat)
            if J["p"]["sheath"] < 0.5 and not style.get("unarmed"):
                self.blade_trail(c, who, t, "#ffffff" if flat else style.get("trail", "#ffffff"))
            c.restore()
        self.broken_pieces(c, t, flat)
        self.head_piece(c, t, flat)
        self.neck_fountain(c, t, "#f4f1ea" if flat else None)
        self.draw_blood(c, vt, "#f4f1ea" if flat else None)
        self.draw_fx(c, vt)
        elements.draw_front(self, c, t, flat)
        if sg <= 0:
            powers.draw_front(self, c, t, vt, flat)
        c.restore()
        if sg > 0:
            c.restore()   # end of the gray layer: the one who stopped time stays in color
            c.save()
            c.translate(W / 2 - cx * z + shx, self.gy + shy)
            c.scale(z, -z)
            self.draw_one(c, sw_who, t, vt, flat)
            powers.draw_front(self, c, t, vt, flat)
            c.restore()
        powers.draw_screen(self, c, t, vt)

        if mode == "slash":
            y = self.gy - 95 * z
            u = min(1, ((vt - self.iai_vt) * FPS - 3) / 4)
            c.drawLine(-10, y + 30 * self.s, W * u, y - 30 * self.s,
                       stroke(col("#ff3b47"), 7 * self.s))
            c.drawLine(-10, y + 30 * self.s, W * u, y - 30 * self.s,
                       stroke(col("#ffffff"), 2.5 * self.s))
        elif self.iai_vt and 0 <= vt - self.iai_vt < 1.4:
            a = max(0, 1 - (vt - self.iai_vt - 0.27) / 1.1)
            y = self.gy - 95 * z
            c.drawLine(-10, y + 30 * self.s, W + 10, y - 30 * self.s,
                       stroke(col("#ff3b47", a * 0.8), 4 * self.s))
        for et, k, d in self.fx:   # twinkle star where the loser flew off
            if k == "twinkle" and 0 <= vt - et < 0.9:
                u = (vt - et) / 0.9
                r = 40 * self.s * math.sin(math.pi * u)
                self.star(c, W * 0.18, H * 0.27, r, 1.0, 4, 7, "#ffd84a")
        c.restore()   # end of camera tilt
        if mode == "normal":
            self.overlay_text(c, vt)

    def overlay_text(self, c, vt):
        W, H, s = self.W, self.H, self.s
        top = (0.16 if not self.wide else 0.13) * H
        (left, lc), (right, rc) = self.f.title
        a = min(1, vt / 0.5)
        fb = self.font_mid if self.wide else self.font_big
        gap = fb.measureText(" vs ")
        wl, wr = fb.measureText(left), fb.measureText(right)
        if wl + gap + wr > W * 0.92:
            fb = skia.Font(typeface("ExtraBold"), fb.getSize() * W * 0.92 / (wl + gap + wr))
            gap = fb.measureText(" vs ")
            wl, wr = fb.measureText(left), fb.measureText(right)
        x0 = W / 2 - (wl + gap + wr) / 2
        c.drawString(left, x0, top, fb, fill(col(lc, a)))
        c.drawString(" vs ", x0 + wl, top, fb, fill(col("#b9b3d6" if self.f.theme == "night" else "#7d6f60", a)))
        c.drawString(right, x0 + wl + gap, top, fb, fill(col(rc, a)))
        self.draw_hp(c, vt)
        for bt, text in self.banners:
            u = vt - bt
            if 0 <= u < 1.0:
                sc = 1 + 1.2 * max(0, 1 - u / 0.12)
                a = min(1, u / 0.06) * min(1, (1.0 - u) / 0.25)
                font = skia.Font(typeface("ExtraBold"), 150 * s * sc)
                y = self.gy - 0.30 * H
                self.text_center(c, text, y + 6 * s, font, "#1b1714", a * 0.6)
                self.text_center(c, text, y, font, "#ffcf3a", a)
        if self.win and vt >= self.win[0]:
            a = min(1, (vt - self.win[0]) / 0.3)
            sc = 1 + 0.4 * max(0, 1 - (vt - self.win[0]) / 0.15)
            font = skia.Font(typeface("ExtraBold"), 80 * s * sc)
            self.text_center(c, self.win[1], top + (200 if self.hp else 150) * s, font,
                             self.win[2], a)

    # ---------------------------------------------------- output
    def render(self, out, stills=None, still_times=()):
        W, H = self.W, self.H
        tmp = tempfile.mkdtemp()
        silent = os.path.join(tmp, "v.mp4")
        wav = os.path.join(tmp, "a.wav")
        dur = self.n / FPS
        mix = audio.mix(self.cues, dur, kit="edit" if self.f.springy else "classic")
        with wave.open(wav, "wb") as w:
            w.setnchannels(2)
            w.setsampwidth(2)
            w.setframerate(audio.SR)
            w.writeframes((np.clip(mix, -1, 1) * 32767).astype(np.int16).tobytes())
        proc = subprocess.Popen(
            ["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgba",
             "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-c:v", "libx264",
             "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", silent],
            stdin=subprocess.PIPE)
        surf = skia.Surface(W, H)
        still_frames = {int(round(st * FPS)) for st in still_times}
        for i in range(self.n):
            c = surf.getCanvas()
            self.render_frame(c, i)
            img = surf.makeImageSnapshot()
            proc.stdin.write(img.toarray(colorType=skia.kRGBA_8888_ColorType).tobytes())
            if stills and i in still_frames:
                img.save(os.path.join(stills, f"frame{i:05d}.png"))
        proc.stdin.close()
        proc.wait()
        subprocess.run(
            ["ffmpeg", "-y", "-v", "error", "-i", silent, "-i", wav, "-c:v", "copy",
             "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "aac", "-b:a", "192k",
             "-ar", "48000", "-shortest", out], check=True)
        return dur


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--fight", default="power", choices=sorted(FIGHTS))
    ap.add_argument("--wide", action="store_true")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--stills")
    ap.add_argument("--still-times", default="")
    a = ap.parse_args()
    r = Renderer(fight=a.fight, wide=a.wide, scale=a.scale)
    times = [float(x) for x in a.still_times.split(",") if x]
    if a.stills:
        os.makedirs(a.stills, exist_ok=True)
    dur = r.render(a.out, a.stills, times)
    print(f"wrote {a.out}: {dur:.1f}s, {r.n} frames")


if __name__ == "__main__":
    main()
