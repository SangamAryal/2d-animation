"""Render a stick-figure sword fight to MP4.

python3 fights/render.py OUT.mp4 [--wide] [--scale 0.5] [--stills DIR]
"""
import argparse
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
import choreo  # noqa: E402
from draw import col, draw_fighter, fill, stroke, polyline  # noqa: E402
from rig import R_HEAD, solve  # noqa: E402
from styles import KASA, RONIN  # noqa: E402

FPS = 60
FONT_DIR = "/usr/share/fonts/opentype/inter/"


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


# ------------------------------------------------------------ helpers
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
    def __init__(self):
        self.R, self.K, self.ev, self.end = choreo.build()
        self.tracks = {"R": (self.R, RONIN), "K": (self.K, KASA)}

    def joints(self, who, t):
        tr, _ = self.tracks[who]
        p, x = tr.sample(t)
        return solve(p, x, tr.facing(t))


# ------------------------------------------------------------ renderer
class Renderer:
    def __init__(self, wide=False, scale=1.0):
        self.wide = wide
        self.W, self.H = (1920, 1080) if wide else (1080, 1920)
        self.W, self.H = int(self.W * scale), int(self.H * scale)
        self.s = scale
        self.gy = self.H * (0.80 if wide else 0.62)
        self.f = Fight()
        self.frames = build_timemap(self.f.ev, self.f.end)
        self.n = len(self.frames)
        self.font_big = skia.Font(typeface("ExtraBold"), 92 * scale)
        self.font_mid = skia.Font(typeface("Bold"), 44 * scale)
        self.font_small = skia.Font(typeface("SemiBold"), 30 * scale)
        self.prepare_events()
        self.prepare_camera()

    # ---------------------------------------------------- events
    def prepare_events(self):
        f = self.f
        self.fx = []      # (video_t, kind, data)
        self.cues = []    # audio cues (video_t, kind, kw)
        self.iai_vt = None
        self.slow_vt = None
        for t, k, kw in f.ev:
            vt = video_time(self.frames, t)
            if k in ("clash", "hit", "ground", "dust"):
                if k == "clash":
                    a, b = f.joints("R", t), f.joints("K", t)
                    pt = seg_closest(a["guard"], a["tip"], b["guard"], b["tip"])
                elif k == "hit":
                    pt = f.joints("R", t)["ftf"]
                else:
                    pt = (kw["x"], 2.0)
                self.fx.append((vt, k, dict(kw, pt=pt, seed=len(self.fx))))
                if k == "clash" and kw.get("big") is not None:
                    pass
            if k == "iai":
                self.iai_vt = vt
                self.iai_t = t
                self.fx.append((vt, "iai", kw))
            if k == "slowmo":
                self.slow_vt = (video_time(self.frames, kw["a0"]),
                                video_time(self.frames, kw["a1"]))
                self.cues.append((self.slow_vt[0], "riser",
                                  dict(dur=self.slow_vt[1] - self.slow_vt[0] + 0.1)))
            if k == "break":
                self.break_t = t
                J = f.joints("K", t)
                self.break_J = J
                self.cues.append((vt, "snap", dict(v=1.0)))
            if k == "winner":
                self.win_vt = vt
                self.win_name = kw["name"]
            if k in ("clash", "hit", "ground", "step", "thud", "draw", "sheathe",
                     "drum", "heart", "iai", "swoosh"):
                self.cues.append((vt, k, kw))
        self.auto_swooshes()

    def auto_swooshes(self):
        f = self.f
        skip = [self.iai_t] if self.iai_vt is not None else []
        for who in ("R", "K"):
            last = -9
            dt = 1 / 240
            t = 0.0
            prev = None
            while t < f.end:
                J = f.joints(who, t)
                tip = J["tip"]
                if prev is not None and J["p"]["sheath"] < 0.5:
                    sp = math.hypot(tip[0] - prev[0], tip[1] - prev[1]) / dt
                    if sp > 1500 and t - last > 0.22 and \
                            all(abs(t - s) > 0.2 for s in skip):
                        v = min(1.0, sp / 4000)
                        self.cues.append((video_time(self.frames, t), "swoosh",
                                          dict(v=0.5 + 0.5 * v,
                                               pitch=0.9 if who == "K" else 1.1)))
                        last = t
                prev = tip
                t += dt

    # ---------------------------------------------------- camera
    def prepare_camera(self):
        f = self.f
        cams = []
        cx, z = None, None
        for i, t in enumerate(self.frames):
            a, b = f.joints("R", t), f.joints("K", t)
            mid = (a["hip"][0] + b["hip"][0]) / 2
            dist = abs(a["hip"][0] - b["hip"][0])
            if self.wide:
                tz = min(self.W / (dist + 650), 3.1 * self.s)
            else:
                tz = min(self.W / (dist + 190), 3.6 * self.s)
            vt = i / FPS
            # slow push-in during the slow motion
            if self.slow_vt and self.slow_vt[0] <= vt <= self.slow_vt[1] + 0.05:
                u = (vt - self.slow_vt[0]) / (self.slow_vt[1] - self.slow_vt[0])
                tz *= 1 + 0.25 * min(1, u)
            if cx is None:
                cx, z = mid, tz
            k = 0.08
            cx += (mid - cx) * k
            # hard cut to the new framing on the white flash of the quick draw
            if self.iai_vt is not None and 0 <= vt - self.iai_vt < 0.2:
                cx, z = mid, tz
            z += (tz - z) * 0.05
            cams.append((cx, z))
        self.cams = cams

    def shake_punch(self, vt):
        sx = sy = 0.0
        punch = 0.0
        for et, k, d in self.fx:
            dt = vt - et
            if dt < 0 or dt > 0.8:
                continue
            m = {"clash": 9, "hit": 12, "ground": 18, "iai": 16}.get(k, 0)
            m *= d.get("v", 1.0) * (1.6 if d.get("big") else 1.0)
            if m == 0:
                continue
            e = math.exp(-dt * 9)
            sx += m * e * math.sin(dt * 87 + d.get("seed", 0))
            sy += m * e * math.cos(dt * 71 + 1.3 * d.get("seed", 0))
            punch += (0.10 if d.get("big") or k == "iai" else 0.04) * math.exp(-dt * 6)
        return sx * self.s, sy * self.s, punch

    # ---------------------------------------------------- background
    def background(self, c, cx, z, dark):
        W, H, gy = self.W, self.H, self.gy
        sky = skia.Paint()
        sky.setShader(skia.GradientShader.MakeLinear(
            [(0, 0), (0, gy)], [col("#eadfcb").toColor(), col("#f7f2e9").toColor()]))
        c.drawRect(skia.Rect(0, 0, W, gy), sky)
        # big sun, slow parallax
        sxp = W / 2 - cx * 0.08 * self.s
        c.drawCircle(sxp, gy - (0.30 if self.wide else 0.22) * H, 0.24 * min(W, H) * 1.25,
                     fill(col("#e6a48f", 0.42)))
        # far ridge
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
        # floor
        fl = skia.Paint()
        fl.setShader(skia.GradientShader.MakeLinear(
            [(0, gy), (0, H)], [col("#e2d5bf").toColor(), col("#cdbb9f").toColor()]))
        c.drawRect(skia.Rect(0, gy, W, H), fl)
        # perspective floor lines that slide with the camera
        lp = stroke(col("#b9a585", 0.55), 2 * self.s)
        step = 140
        k0 = int((cx - W / z) // step) - 2
        for k in range(k0, k0 + int(2 * W / z / step) + 6):
            sx = W / 2 + (k * step - cx) * z
            bx = W / 2 + (sx - W / 2) * 3.2
            c.drawLine(sx, gy, bx, H, lp)
        for j in range(1, 6):
            yy = gy + (H - gy) * (j / 6) ** 1.6
            c.drawLine(0, yy, W, yy, stroke(col("#b9a585", 0.35), 1.5 * self.s))
        c.drawLine(0, gy, W, gy, stroke(col("#2a2622"), 3.5 * self.s))
        if dark > 0:
            c.drawRect(skia.Rect(0, 0, W, H), fill(col("#120e14", dark)))

    # ---------------------------------------------------- frame
    def tails(self, who, t):
        f = self.f
        pts_a, pts_b = [], []
        for k in range(7):
            J = f.joints(who, t - k * 0.035)
            hx, hy = J["head"]
            fc = J["facing"]
            flut = math.sin(t * 13 + k * 0.9) * k * 1.4
            base = (hx - fc * (R_HEAD - 2), hy + 3)
            pts_a.append((base[0] - fc * k * 7, base[1] - k * 1.2 + flut))
            pts_b.append((base[0] - fc * k * 6, base[1] - k * 3.2 - flut * 0.8))
        # anchor first point on the head now
        J = f.joints(who, t)
        hx, hy = J["head"]
        fc = J["facing"]
        pts_a[0] = pts_b[0] = (hx - fc * (R_HEAD - 2), hy + 3)
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
                    a = 0.75 * (1 - k / N) ** 1.3
                    c.drawPath(path, fill(col(color, a)))
            prev = (tip, base)

    def ghosts(self, c, who, t, style, flat):
        f = self.f
        a, b = f.joints(who, t), f.joints(who, t - 1 / 60)
        sp = abs(a["hip"][0] - b["hip"][0]) * 60
        if sp < 700:
            return
        for k in range(1, 6):
            J = f.joints(who, t - k * 0.012)
            draw_fighter(c, J, style, alpha=0.32 * (1 - k / 6), flat=flat)

    def draw_fx(self, c, vt):
        for et, k, d in self.fx:
            dt = vt - et
            if dt < 0:
                continue
            rng = np.random.default_rng(d.get("seed", 0) + 11)
            px, py = d.get("pt", (0, 0))
            if k == "clash" and dt < 0.45:
                big = d.get("big", False)
                n = 26 if big else 14
                for i in range(n):
                    ang = rng.uniform(0, 2 * math.pi)
                    spd = rng.uniform(250, 900) * (1.3 if big else 1)
                    vx, vy = math.cos(ang) * spd, math.sin(ang) * spd + 150
                    x = px + vx * dt
                    y = py + vy * dt - 700 * dt * dt
                    life = rng.uniform(0.18, 0.42)
                    if dt > life:
                        continue
                    a = 1 - dt / life
                    tx, ty = x - vx * 0.025, y - (vy - 1400 * dt) * 0.025
                    c.drawLine(x, y, tx, ty, stroke(col("#ffd36b", a), 2.6))
                if dt < 0.14:
                    r = (30 if big else 18) + dt * 500
                    a = 1 - dt / 0.14
                    self.star(c, px, py, r, a, 8 if big else 6, d.get("seed", 0))
            elif k == "hit" and dt < 0.35:
                for i in range(10):
                    ang = rng.uniform(-0.8, 0.8) + (0 if rng.random() < 0.5 else 0)
                    ln = rng.uniform(40, 90)
                    r0 = 15 + dt * 300
                    a = 1 - dt / 0.35
                    x0, y0 = px + math.cos(ang) * r0, py + math.sin(ang) * r0
                    c.drawLine(x0, y0, x0 + math.cos(ang) * ln * a,
                               y0 + math.sin(ang) * ln * a,
                               stroke(col("#1b1b1f", a), 4))
                if dt < 0.12:
                    self.star(c, px, py, 26 + dt * 400, 1 - dt / 0.12, 7, 3)
            elif k in ("dust", "ground") and dt < 1.0:
                v = d.get("v", 1.0) * (1.6 if k == "ground" else 1.0)
                for i in range(int(8 * v) + 3):
                    side = -1 if i % 2 else 1
                    spd = rng.uniform(40, 160) * v
                    x = px + side * spd * (1 - math.exp(-dt * 4)) / 1.2
                    y = 4 + rng.uniform(5, 30) * dt * v + 8
                    r = (6 + 28 * v * (1 - math.exp(-dt * 5))) * rng.uniform(0.7, 1.2)
                    a = 0.45 * (1 - dt / 1.0) ** 1.5
                    c.drawCircle(x, y, r, fill(col("#b9a17e", a)))
                if k == "ground" and dt < 1.6:
                    a = 0.9 * (1 - dt / 1.6)
                    for i in range(7):
                        side = -1 if i % 2 else 1
                        x = px
                        pts = [(x, 1)]
                        for j in range(4):
                            x += side * rng.uniform(14, 34)
                            pts.append((x, 1 - rng.uniform(1, 7) * (j + 1) * 0.6))
                        polyline(c, pts, stroke(col("#3a3128", a), 2.4))

    def star(self, c, x, y, r, a, n, seed):
        rng = np.random.default_rng(seed + 99)
        path = skia.Path()
        rot = rng.uniform(0, 1)
        for i in range(2 * n):
            rr = r if i % 2 == 0 else r * 0.28
            ang = (i / (2 * n) + rot) * 2 * math.pi
            px, py = x + math.cos(ang) * rr, y + math.sin(ang) * rr
            if i == 0:
                path.moveTo(px, py)
            else:
                path.lineTo(px, py)
        path.close()
        c.drawPath(path, fill(col("#ffffff", a)))
        c.drawPath(path, stroke(col("#ffcf5a", a), 2))

    def broken_piece(self, c, t, flat):
        if not hasattr(self, "break_t") or t < self.break_t:
            return
        J = self.break_J
        g, tip = J["guard"], J["tip"]
        dx, dy = tip[0] - g[0], tip[1] - g[1]
        L = math.hypot(dx, dy)
        ux, uy = dx / L, dy / L
        p0 = (g[0] + ux * 34, g[1] + uy * 34)
        cx0, cy0 = (p0[0] + tip[0]) / 2, (p0[1] + tip[1]) / 2
        half = (L - 34) / 2
        ang0 = math.atan2(uy, ux)
        # simple fall with spin, then rest on the ground
        x, y, vx, vy, a, w = cx0, cy0, -J["facing"] * 50, 60, ang0, 7.0
        dt = 1 / 240
        tt = 0
        while tt < t - self.break_t:
            vy -= 1100 * dt
            x += vx * dt
            y += vy * dt
            a += w * dt
            low = y - abs(math.sin(a)) * half
            if low <= 1.5 and vy < 0:
                y = 1.5 + abs(math.sin(a)) * half
                vy = -vy * 0.25
                vx *= 0.5
                w *= 0.4
                if abs(vy) < 40:
                    vy = 0
                    # settle flat
                    a += (round(a / math.pi) * math.pi - a) * 0.2
            tt += dt
        ex, ey = math.cos(a) * half, math.sin(a) * half
        c.drawLine(x - ex, y - ey, x + ex, y + ey, stroke(col(flat or "#222222"), 5.2))
        c.drawLine(x - ex, y - ey, x + ex, y + ey, stroke(col(flat or "#e9eef2"), 2.6))

    def text_center(self, c, s, y, font, color, a=1.0, x=None):
        w = font.measureText(s)
        p = fill(col(color, a))
        c.drawString(s, (x if x is not None else self.W / 2) - w / 2, y, font, p)

    def render_frame(self, c, i):
        f = self.f
        t = self.frames[i]
        vt = i / FPS
        cx, z = self.cams[i]
        shx, shy, punch = self.shake_punch(vt)
        z *= 1 + punch
        W, H = self.W, self.H

        # impact-frame modes
        mode = "normal"
        for et, k, d in self.fx:
            dtf = (vt - et) * FPS
            if k in ("clash", "hit") and d.get("big") and 0 <= dtf < 3:
                mode = "invert"
            if k == "iai":
                if 0 <= dtf < 3:
                    mode = "white"
                elif 3 <= dtf < 16:
                    mode = "slash"
        dark = 0.0
        if self.slow_vt and self.slow_vt[0] <= vt < (self.iai_vt or 0):
            u = (vt - self.slow_vt[0]) / max(1e-3, self.iai_vt - self.slow_vt[0])
            dark = 0.35 * min(1, u * 2)
        if self.iai_vt and 0 <= vt - self.iai_vt < 2.0 and mode == "normal":
            dark = 0.35 * max(0, 1 - (vt - self.iai_vt - 0.27) / 1.2)

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
        # shadows
        if not flat:
            for who in ("R", "K"):
                J = f.joints(who, t)
                h = J["hip"][1]
                sa = max(0.08, 0.28 - h / 900)
                c.drawOval(skia.Rect(J["hip"][0] - 34, -5, J["hip"][0] + 34, 5),
                           fill(col("#3a2e22", sa)))
        if not flat:
            self.draw_fx_ground(c, vt)
        for who in ("K", "R"):
            tr, style = f.tracks[who]
            self.ghosts(c, who, t, style, flat or ("#d8323c" if who == "R" else "#5b72ad"))
            J = f.joints(who, t)
            tails = self.tails(who, t) if style.get("band") else None
            draw_fighter(c, J, style, flat=flat, tails=tails)
            if J["p"]["sheath"] < 0.5:
                self.blade_trail(c, who, t, "#ffffff" if flat else
                                 ("#ffd9d9" if who == "R" else "#dbe6ff"))
        self.broken_piece(c, t, flat)
        self.draw_fx(c, vt)
        c.restore()

        if mode == "slash":
            # one long cut line across the screen at blade height
            y = self.gy - 95 * z
            u = min(1, ((vt - self.iai_vt) * FPS - 3) / 4)
            p = stroke(col("#ff3b47"), 7 * self.s)
            c.drawLine(-10, y + 30 * self.s, W * u, y - 30 * self.s, p)
            c.drawLine(-10, y + 30 * self.s, W * u, y - 30 * self.s,
                       stroke(col("#ffffff"), 2.5 * self.s))
        elif self.iai_vt and 0 <= vt - self.iai_vt < 1.4:
            a = max(0, 1 - (vt - self.iai_vt - 0.27) / 1.1)
            y = self.gy - 95 * z
            c.drawLine(-10, y + 30 * self.s, W + 10, y - 30 * self.s,
                       stroke(col("#ff3b47", a * 0.8), 4 * self.s))
        if mode == "normal":
            self.overlay_text(c, vt)

    def draw_fx_ground(self, c, vt):
        pass

    def overlay_text(self, c, vt):
        W, H, s = self.W, self.H, self.s
        top = (0.16 if not self.wide else 0.13) * H
        left, right = choreo.TITLE
        a = min(1, vt / 0.5)
        if self.wide:
            fb = self.font_mid
        else:
            fb = self.font_big
        gap = fb.measureText(" vs ")
        wl, wr = fb.measureText(left), fb.measureText(right)
        x0 = W / 2 - (wl + gap + wr) / 2
        c.drawString(left, x0, top, fb, fill(col("#2f4a8c", a)))
        c.drawString(" vs ", x0 + wl, top, fb, fill(col("#7d6f60", a)))
        c.drawString(right, x0 + wl + gap, top, fb, fill(col("#d8323c", a)))
        # name tags over heads at the start
        if vt < 3.0:
            ta = min(1, vt / 0.4) * min(1, (3.0 - vt) / 0.5)
            i = int(vt * FPS)
            cx, z = self.cams[i]
            t = self.frames[i]
            for who, name, color in (("R", "RONIN", "#17171c"), ("K", "KASA", "#2f4a8c")):
                J = self.f.joints(who, t)
                hx, hy = J["head"]
                sx = W / 2 + (hx - cx) * z
                sy = self.gy - (hy + 55) * z
                self.text_center(c, name, sy, self.font_small, color, ta, x=sx)
        if hasattr(self, "win_vt") and vt >= self.win_vt:
            a = min(1, (vt - self.win_vt) / 0.4)
            y = top + (150 if not self.wide else 90) * s
            self.text_center(c, f"{self.win_name} WINS", y, self.font_mid, "#d8323c", a)

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
            w.writeframes((mix * 32767).astype(np.int16).tobytes())
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
    ap.add_argument("--wide", action="store_true")
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--stills")
    ap.add_argument("--still-times", default="")
    a = ap.parse_args()
    r = Renderer(wide=a.wide, scale=a.scale)
    times = [float(x) for x in a.still_times.split(",") if x]
    if a.stills:
        os.makedirs(a.stills, exist_ok=True)
    dur = r.render(a.out, a.stills, times)
    print(f"wrote {a.out}: {dur:.1f}s, {r.n} frames")


if __name__ == "__main__":
    main()
