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
from draw import col, draw_fighter, fill, stroke, polyline  # noqa: E402
from rig import R_HEAD, solve  # noqa: E402

FPS = 60
FONT_DIR = "/usr/share/fonts/opentype/inter/"
FIGHTS = {"patience": "choreo", "power": "choreo_power"}


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
        self.tracks = {i: (tr, st) for i, tr, st in self.fighters}
        self.ids = [i for i, _, _ in self.fighters]

    def joints(self, who, t):
        tr, st = self.tracks[who]
        p, x = tr.sample(t)
        return solve(p, x, tr.facing(t), size=st.get("size", 1.0),
                     blade=st.get("blade", 72))

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
        for t, k, kw in f.ev:
            vt = video_time(self.frames, t)
            seed = len(self.fx)
            if k == "clash":
                a, b = f.joints(f.ids[0], t), f.joints(f.ids[1], t)
                pt = seg_closest(a["guard"], a["tip"], b["guard"], b["tip"])
                self.fx.append((vt, k, dict(kw, pt=pt, seed=seed)))
            elif k == "hit":
                A = f.joints(kw["by"], t)
                if kw.get("part"):
                    pt = A[kw["part"]]
                else:
                    B = f.joints(kw["on"], t)
                    pt = seg_closest(A["guard"], A["tip"], B["hip"], B["neck"])
                self.fx.append((vt, k, dict(kw, pt=pt, seed=seed)))
            elif k == "slam":
                A = f.joints(kw["by"], t)
                self.fx.append((vt, k, dict(kw, pt=(A["tip"][0], 2.0), seed=seed)))
            elif k in ("ground", "dust", "skid", "gust", "stomp"):
                self.fx.append((vt, k, dict(kw, pt=(kw["x"], 2.0), seed=seed)))
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
            elif k == "focus":
                end = kw.get("until")
                self.focus.append((vt, video_time(self.frames, end) if end else 1e9,
                                   kw["who"]))
            elif k in ("twinkle", "charge"):
                self.fx.append((vt, k, dict(kw, seed=seed)))
                if k == "charge":
                    self.cues.append((vt, "riser", dict(dur=kw["dur"])))
            self.cues.append((vt, k, kw))
        self.auto_swooshes()

    def auto_swooshes(self):
        f = self.f
        skip = [self.iai_t] if self.iai_vt is not None else []
        for who in f.ids:
            st = f.tracks[who][1]
            heavy = st.get("sword") == "cleaver"
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
                            all(abs(t - s) > 0.2 for s in skip):
                        self.cues.append((video_time(self.frames, t), "swoosh",
                                          dict(v=min(1.0, 0.5 + sp / 6000),
                                               heavy=heavy)))
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
            foc = [w for a, b, w in self.focus if a <= vt < b]
            if foc:
                J = f.joints(foc[0], t)
                mid, dist = J["hip"][0], 160
            else:
                mid, dist = (min(xs) + max(xs)) / 2, max(xs) - min(xs)
            if self.wide:
                tz = min(self.W / (dist + 700), 2.8 * self.s)
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

    def shake_punch(self, vt):
        sx = sy = punch = 0.0
        for et, k, d in self.fx:
            dt = vt - et
            if dt < 0 or dt > 1.0:
                continue
            m = {"clash": 8, "hit": 4, "slam": 34, "stomp": 7, "iai": 16}.get(k, 0)
            m *= d.get("v", 1.0) * (2.0 if d.get("big") else 1.0)
            if m == 0:
                continue
            e = math.exp(-dt * (6 if k == "slam" else 9))
            sx += m * e * math.sin(dt * 87 + d.get("seed", 0))
            sy += m * e * math.cos(dt * 71 + 1.3 * d.get("seed", 0))
            if k in ("slam", "iai") or d.get("big"):
                punch += 0.12 * math.exp(-dt * 6)
        return sx * self.s, sy * self.s, punch

    # ---------------------------------------------------- background
    def background(self, c, cx, z, dark):
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
        return pts_a, pts_b

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
        for et, k, d in self.fx:
            dt = vt - et
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

    def broken_pieces(self, c, t, flat):
        for bt, who, J in self.breaks:
            if t < bt:
                continue
            g, tip = J["guard"], J["tip"]
            dx, dy = tip[0] - g[0], tip[1] - g[1]
            L = math.hypot(dx, dy)
            ux, uy = dx / L, dy / L
            cut = 34 * J["size"]
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
            c.drawLine(x - ex, y - ey, x + ex, y + ey, stroke(col(flat or "#222222"), 5.2))
            c.drawLine(x - ex, y - ey, x + ex, y + ey, stroke(col(flat or "#e9eef2"), 2.6))

    def text_center(self, c, s, y, font, color, a=1.0, x=None):
        w = font.measureText(s)
        c.drawString(s, (x if x is not None else self.W / 2) - w / 2, y, font,
                     fill(col(color, a)))

    # ---------------------------------------------------- frame
    def render_frame(self, c, i):
        f = self.f
        t = self.frames[i]
        vt = i / FPS
        cx, z = self.cams[i]
        shx, shy, punch = self.shake_punch(vt)
        z *= 1 + punch
        W, H = self.W, self.H

        mode = "normal"
        for et, k, d in self.fx:
            dtf = (vt - et) * FPS
            if (k in ("clash", "hit") and d.get("big") or k == "slam") and 0 <= dtf < 3:
                mode = "invert"
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
        if mode in ("invert", "slash"):
            c.clear(col("#0d0b10"))
        else:
            self.background(c, cx, z, dark)

        flat = "#f4f1ea" if mode in ("invert", "slash") else None
        c.save()
        c.translate(W / 2 - cx * z + shx, self.gy + shy)
        c.scale(z, -z)
        if not flat:
            for who in f.ids:
                J = f.joints(who, t)
                S = J["size"]
                h = J["hip"][1]
                sa = max(0.0, 0.28 - h / 900)
                c.drawOval(skia.Rect(J["hip"][0] - 34 * S, -5, J["hip"][0] + 34 * S, 5),
                           fill(col("#3a2e22", sa)))
        for who in f.ids:
            tr, style = f.tracks[who]
            if not flat and style.get("fast"):
                self.speed_lines(c, who, t, style["ghost"])
            self.ghosts(c, who, t, style, flat or style.get("ghost", "#888888"))
            J = f.joints(who, t)
            tails = self.tails(who, t) if style.get("band") else None
            draw_fighter(c, J, style, flat=flat, tails=tails)
            if J["p"]["sheath"] < 0.5:
                self.blade_trail(c, who, t, "#ffffff" if flat else style.get("trail", "#ffffff"))
        self.broken_pieces(c, t, flat)
        self.draw_fx(c, vt)
        c.restore()

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
        x0 = W / 2 - (wl + gap + wr) / 2
        c.drawString(left, x0, top, fb, fill(col(lc, a)))
        c.drawString(" vs ", x0 + wl, top, fb, fill(col("#7d6f60", a)))
        c.drawString(right, x0 + wl + gap, top, fb, fill(col(rc, a)))
        if self.win and vt >= self.win[0]:
            a = min(1, (vt - self.win[0]) / 0.3)
            sc = 1 + 0.4 * max(0, 1 - (vt - self.win[0]) / 0.15)
            font = skia.Font(typeface("ExtraBold"), 80 * s * sc)
            self.text_center(c, self.win[1], top + 150 * s, font, self.win[2], a)

    # ---------------------------------------------------- output
    def render(self, out, stills=None, still_times=()):
        W, H = self.W, self.H
        tmp = tempfile.mkdtemp()
        silent = os.path.join(tmp, "v.mp4")
        wav = os.path.join(tmp, "a.wav")
        dur = self.n / FPS
        mix = audio.mix(self.cues, dur)
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
