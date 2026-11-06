"""Draws the volcano-vs-snowstorm sim with Skia (flat, layered night scene)."""
from __future__ import annotations

import math
import subprocess
import sys
from pathlib import Path

import numpy as np
import skia

sys.path.insert(0, str(Path(__file__).parent.parent / "katana"))
from render import font, hex2color  # noqa: E402  (shared helpers + bundled fonts)

from volcano_sim import H, W, slope_y  # noqa: E402

RULES = ["Every snowflake that lands in the crater", "cools the lava 10%.",
         "Every lava bomb that falls back in heats it 50%", "and launches 2 more."]


def lerp_color(a: str, b: str, t: float, alpha: int = 255) -> int:
    a, b = a.lstrip("#"), b.lstrip("#")
    ca = [int(a[i:i + 2], 16) for i in (0, 2, 4)]
    cb = [int(b[i:i + 2], 16) for i in (0, 2, 4)]
    c = [int(ca[k] + (cb[k] - ca[k]) * t) for k in range(3)]
    return skia.Color(c[0], c[1], c[2], alpha)


def mountains(rng, base_y, amp, step, jag):
    p = skia.Path()
    p.moveTo(-20, H)
    x = -20
    y = base_y
    while x < W + 40:
        y = base_y - amp * (0.5 + 0.5 * math.sin(x / 210 + rng.uniform(0, 0.5))) - rng.uniform(0, jag)
        p.lineTo(x, y)
        x += step
    p.lineTo(W + 40, H)
    p.close()
    return p


def pine(c, x, base, h, col, snow):
    w = h * 0.42
    p = skia.Path()
    for k in range(3):
        top = base - h + k * h * 0.26
        bw = w * (0.55 + 0.25 * k)
        p.moveTo(x, top)
        p.lineTo(x - bw, top + h * 0.42)
        p.lineTo(x + bw, top + h * 0.42)
        p.close()
    c.drawPath(p, skia.Paint(AntiAlias=True, Color=col))
    s = skia.Path()
    s.moveTo(x, base - h)
    s.lineTo(x - w * 0.3, base - h + h * 0.16)
    s.lineTo(x + w * 0.3, base - h + h * 0.16)
    s.close()
    c.drawPath(s, skia.Paint(AntiAlias=True, Color=snow))


class VolcanoRenderer:
    def __init__(self, sim):
        self.sim = sim
        self.cfg = sim["cfg"]
        rng = np.random.default_rng(4)
        cfg = self.cfg
        self.f_rule = font("InterDisplay-Bold.otf", 40)
        self.f_meter = font("InterDisplay-Black.otf", 120)
        self.f_label = font("InterDisplay-Bold.otf", 34)
        self.stars = [(rng.uniform(0, W), rng.uniform(0, 1000), rng.uniform(0.8, 2.2), rng.uniform(0, 6.28))
                      for _ in range(140)]
        self.far = mountains(rng, 1230, 160, 60, 40)
        self.near = mountains(rng, 1380, 110, 45, 30)
        # volcano cone
        cx, cy, ch = cfg.crater_x, cfg.crater_y, cfg.crater_half
        cone = skia.Path()
        left_d = (cfg.ground_y - cy - 8) / cfg.slope
        cone.moveTo(cx - ch - left_d - 40, cfg.ground_y + 4)
        cone.lineTo(cx - ch - 18, cy - 6)
        cone.quadTo(cx - ch, cy - 22, cx - ch + 14, cy - 4)
        cone.lineTo(cx + ch - 14, cy - 4)
        cone.quadTo(cx + ch, cy - 22, cx + ch + 18, cy - 6)
        cone.lineTo(cx + ch + left_d + 40, cfg.ground_y + 4)
        cone.close()
        self.cone = cone
        # snow cap patches: top edge follows the slope, lower edge is jagged
        self.caps = []
        for side in (-1, 1):
            cap = skia.Path()
            x0 = cx + side * (ch + 14)
            cap.moveTo(x0, cy - 4)
            xs = [cx + side * (ch + 14 + d) for d in np.linspace(0, 330, 12)]
            for x in xs:
                cap.lineTo(x, float(slope_y(cfg, np.array([x]))[0]) - 2)
            for j, x in enumerate(xs[::-1]):
                depth = 26 + 34 * (0.5 + 0.5 * math.sin(j * 1.9)) + (1 - j / 11) * 30
                cap.lineTo(x - side * 18, float(slope_y(cfg, np.array([x]))[0]) + depth)
            cap.close()
            self.caps.append(cap)
        # lava rivers (precomputed polylines down each side)
        self.rivers = []
        for side, off in [(-1, 0.25), (1, 0.6), (-1, 0.75), (1, 0.15)]:
            pts = []
            x = cx + side * (ch - 10 - 30 * off)
            for k in range(60):
                d = abs(x - cx)
                y = float(slope_y(cfg, np.array([x]))[0]) - 4
                pts.append((x, y))
                x += side * (9 + 4 * math.sin(k * 0.7 + off * 10))
            self.rivers.append(pts)
        self.trees = [(rng.uniform(0, 1) < 0.5) for _ in range(1)]
        self.tree_pos = sorted([(rng.uniform(-20, 300), rng.uniform(110, 190)) for _ in range(5)] +
                               [(rng.uniform(780, 1100), rng.uniform(110, 190)) for _ in range(5)])
        self.meter_kick = 0.0
        self.spray = []  # decorative lava spray: x, y, vx, vy, born
        self.rng = np.random.default_rng(9)
        self.meter_tint = 0.0

    def hot(self, heat):
        return min(1.0, max(0.0, (math.log10(max(heat, 1)) - 2.0) / 5.5))

    def frame(self, fi, surf):
        c = surf.getCanvas()
        fr = self.sim["frames"][fi]
        cfg = self.cfg
        heat = fr["heat"]
        h = self.hot(heat)
        cold = min(1.0, max(0.0, (100 - heat) / 85))  # 0 at 100%, 1 near 15%
        t = fr["t"]
        er = fr["erupt"]
        ex = 0.0 if er is None else min(1.0, er / 2.5)

        shake = 0.0
        if heat > 500:
            shake = min(14.0, 2 * math.log10(heat / 500 + 1) * 3) + 18 * ex
        sx = shake * math.sin(t * 53.0) * 0.6
        sy = shake * math.cos(t * 41.0) * 0.6
        c.save()
        c.translate(sx, sy)

        # sky
        top = lerp_color("#070A1A", "#2A0A06", h)
        mid = lerp_color("#151B3A", "#7A1E0C", h)
        bot = lerp_color("#2B2550", "#E0581A", h)
        c.drawRect(skia.Rect(-40, -40, W + 40, H + 40), skia.Paint(Shader=skia.GradientShader.MakeLinear(
            [(0, 0), (0, 1450)], [top, mid, bot], [0, 0.6, 1])))
        star_a = int(255 * (1 - h) * 0.9)
        for (x, y, r, ph) in self.stars:
            a = int(star_a * (0.6 + 0.4 * math.sin(t * 2 + ph)))
            if a > 4:
                c.drawCircle(x, y, r, skia.Paint(AntiAlias=True, Color=skia.Color(230, 235, 255, a)))
        # back mountains
        c.drawPath(self.far, skia.Paint(AntiAlias=True, Color=lerp_color("#1C1F3D", "#3D1410", h)))
        c.drawPath(self.near, skia.Paint(AntiAlias=True, Color=lerp_color("#151731", "#2C0E0A", h)))

        # glow behind the crater
        glow_r = 300 + 480 * h + 900 * ex
        ga = int(60 + 150 * h + 40 * (1 - cold))
        c.drawCircle(cfg.crater_x, cfg.crater_y, glow_r, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
            (cfg.crater_x, cfg.crater_y), glow_r, [lerp_color("#FF7A1A", "#FFD36B", h, min(255, ga)),
                                                   hex2color("#FF4A10", 0)], [0, 1])))

        # eruption column (behind the cone so it rises out of the crater)
        if er is not None:
            colw = 140 + 900 * ex
            col = skia.Path()
            col.moveTo(cfg.crater_x - cfg.crater_half * 0.7, cfg.crater_y)
            col.lineTo(cfg.crater_x - colw, -60)
            col.lineTo(cfg.crater_x + colw, -60)
            col.lineTo(cfg.crater_x + cfg.crater_half * 0.7, cfg.crater_y)
            col.close()
            c.drawPath(col, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
                [(0, cfg.crater_y), (0, 0)], [hex2color("#FFF3C4", 255), hex2color("#FFB23A", int(200 * ex + 55))], [0, 1])))

        # cone, lit from the crater
        c.drawPath(self.cone, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
            [(0, cfg.crater_y), (0, cfg.ground_y)],
            [lerp_color("#3A2A3A", "#7A2A14", h), lerp_color("#1C1524", "#2A0F0C", h)], [0, 1])))
        snow_a = int(255 * max(0.0, 1 - h * 2.2))
        if snow_a > 0:
            for cap in self.caps:
                c.drawPath(cap, skia.Paint(AntiAlias=True, Color=skia.Color(236, 242, 255, snow_a)))

        # lava pool in the crater
        pool_col = lerp_color("#8A1A10", "#FF8A1A", min(1, heat / 150)) if heat < 150 else \
            lerp_color("#FF8A1A", "#FFF0A0", h)
        pr = skia.Rect(cfg.crater_x - cfg.crater_half + 10, cfg.crater_y - 14, cfg.crater_x + cfg.crater_half - 10, cfg.crater_y + 10)
        c.drawOval(pr, skia.Paint(AntiAlias=True, Color=pool_col))
        for k in range(5):
            bx = cfg.crater_x + math.sin(t * 1.3 + k * 2.1) * (cfg.crater_half - 30)
            br = 4 + 3 * (0.5 + 0.5 * math.sin(t * 3 + k))
            c.drawCircle(bx, cfg.crater_y - 4, br, skia.Paint(AntiAlias=True, Color=lerp_color("#FFB347", "#FFFFFF", h, 200)))

        # lava rivers once it's roaring
        flow = max(0.0, min(1.0, (math.log10(max(heat, 1)) - math.log10(250)) / 3.5))
        if flow > 0:
            for k, pts in enumerate(self.rivers):
                n = max(2, int(len(pts) * min(1.0, flow * (1.1 - 0.15 * k))))
                path = skia.Path()
                path.moveTo(*pts[0])
                for p in pts[1:n]:
                    path.lineTo(*p)
                c.drawPath(path, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=26,
                                            StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join,
                                            Color=hex2color("#FF6A1A", 120),
                                            MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 10)))
                c.drawPath(path, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=12,
                                            StrokeCap=skia.Paint.kRound_Cap, StrokeJoin=skia.Paint.kRound_Join,
                                            Color=hex2color("#FFB347")))

        # ground + trees
        c.drawRect(skia.Rect(-40, cfg.ground_y, W + 40, H + 40), skia.Paint(Shader=skia.GradientShader.MakeLinear(
            [(0, cfg.ground_y), (0, H)], [lerp_color("#1A1830", "#3A120A", h), lerp_color("#0B0A16", "#150604", h)], [0, 1])))
        c.drawRect(skia.Rect(-40, cfg.ground_y - 6, W + 40, cfg.ground_y + 10),
                   skia.Paint(Color=lerp_color("#DDE6FF", "#FF9A4A", h, int(255 * max(0.25, 1 - h)))))
        for (x, th) in self.tree_pos:
            pine(c, x, cfg.ground_y + 6, th * 1.6, lerp_color("#0E1226", "#1A0806", h),
                 skia.Color(230, 238, 255, snow_a))

        # bombs
        for (x, y, st, age) in fr["bombs"]:
            if st == 0:
                col_core, col_glow, rr = hex2color("#FFF1B8"), hex2color("#FF7A1A", 120), 9
            else:
                k = min(1.0, age / 2.4)
                col_core = lerp_color("#FF8A2A", "#3A1410", k)
                col_glow = lerp_color("#FF5A1A", "#200A08", k, int(110 * (1 - k)))
                rr = 9
            c.drawCircle(x, y, rr * 2.2, skia.Paint(AntiAlias=True, Color=col_glow,
                                                    MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 6)))
            c.drawCircle(x, y, rr, skia.Paint(AntiAlias=True, Color=col_core))

        # decorative spray once the lava is roaring
        rate = 0 if heat < 800 else 30 + 260 * h + 400 * ex
        for _ in range(self.rng.poisson(rate / cfg.fps)):
            self.spray.append([cfg.crater_x + self.rng.uniform(-60, 60), cfg.crater_y - 6,
                               self.rng.normal(0, 260 + 300 * ex), -self.rng.uniform(900, 1700 + 900 * ex), t])
        dt = 1.0 / cfg.fps
        alive = []
        for p in self.spray:
            p[3] += cfg.gravity * dt
            p[0] += p[2] * dt
            p[1] += p[3] * dt
            if p[1] < H + 20 and t - p[4] < 3:
                alive.append(p)
                c.drawCircle(p[0], p[1], 12, skia.Paint(AntiAlias=True, Color=hex2color("#FF7A1A", 90),
                                                        MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 5)))
                c.drawCircle(p[0], p[1], 6, skia.Paint(AntiAlias=True, Color=hex2color("#FFE08A")))
        self.spray = alive

        # splashes
        for (x, y, t0) in fr["splashes"]:
            k = (t - t0) / 0.5
            c.drawCircle(x, y - 6, 10 + 50 * k, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                                           StrokeWidth=5 * (1 - k) + 1, Color=hex2color("#FFD36B", int(230 * (1 - k)))))
            for j in range(6):
                a = -math.pi * (0.15 + 0.7 * j / 5)
                d = 70 * k
                c.drawCircle(x + math.cos(a) * d, y - 6 + math.sin(a) * d + 120 * k * k, 4 * (1 - k) + 1,
                             skia.Paint(AntiAlias=True, Color=hex2color("#FFB347", int(255 * (1 - k)))))

        # snow
        for (x, y, s) in fr["deco"]:
            c.drawCircle(x, y, s, skia.Paint(AntiAlias=True, Color=skia.Color(235, 240, 255, 150)))
        for (x, y, s) in fr["flakes"]:
            self.snowbuddy(c, x, y, s, t, heat)

        # steam
        for (x, y, t0, sz) in fr["steam"]:
            k = (t - t0) / 1.4
            for j in range(3):
                r = (14 + 30 * k) * sz * (0.8 + 0.2 * j)
                c.drawCircle(x + (j - 1) * 14 * sz, y - 70 * k * sz - j * 8, r,
                             skia.Paint(AntiAlias=True, Color=skia.Color(210, 214, 228, int(150 * (1 - k)))))

        c.restore()

        # eruption whiteout
        if er is not None:
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=skia.Color(255, 190, 90, int(165 * ex ** 1.5))))

        # text: rules + meter
        y = 220
        for i, line in enumerate(RULES):
            self.text(c, line, self.f_rule, y + i * 52, hex2color("#FFFFFF"))
        if fr["cool"]:
            self.meter_tint = 1.0
        if fr["heatup"]:
            self.meter_tint = -1.0
            self.meter_kick = 1.0
        self.meter_kick *= 0.85
        self.meter_tint *= 0.88
        base = lerp_color("#9FD4FF", "#FFB347", min(1, max(0, (heat - 20) / 80)))
        if self.meter_tint > 0.1:
            base = lerp_color("#FFB347", "#BFE6FF", self.meter_tint) if heat > 60 else base
        if er is not None:
            base = lerp_color("#FFB347", "#FFFFFF", ex)
        txt = f"{heat:,.0f}%"
        sc = 1 + 0.12 * self.meter_kick
        c.save()
        c.translate(W / 2, 470)
        c.scale(sc, sc)
        c.translate(-W / 2, -470)
        self.text(c, txt, self.f_meter, 510, base, outline=True)
        c.restore()
        self.text(c, "LAVA HEAT", self.f_label, 560, hex2color("#FFFFFF", 200))

        # fade in/out
        n = len(self.sim["frames"])
        fade = min(1.0, fi / 10, (n - fi) / 30)
        if fade < 1:
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=skia.Color(0, 0, 0, int(255 * (1 - fade)))))

    def snowbuddy(self, c, x, y, s, t, heat):
        """A little snowball character: crystal crown, face, cheeks. Panics near the hot crater."""
        cfg = self.cfg
        r = s * 4.2                     # 23-34 px
        seed = (x * 7.3 + s * 13.1) % 6.28
        wob = math.sin(t * 3.2 + seed) * 0.18
        near = max(0.0, 1 - abs(y - cfg.crater_y) / 260) * (1 if abs(x - cfg.crater_x) < cfg.crater_half * 1.8 else 0)
        scared = near > 0.15
        shiver = (math.sin(t * 60 + seed) * 2.0 * near) if scared else 0.0
        c.save()
        c.translate(x + shiver, y)
        c.rotate(math.degrees(wob))
        # cold glow so it reads against the dark sky
        c.drawCircle(0, 0, r * 1.9, skia.Paint(AntiAlias=True, Color=skia.Color(150, 205, 255, 70),
                                               MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 9)))
        # crystal crown
        crown = skia.Paint(AntiAlias=True, StrokeWidth=3, StrokeCap=skia.Paint.kRound_Cap, Color=hex2color("#CFEAFF"))
        for k in range(-1, 2):
            a = -math.pi / 2 + k * 0.55
            ex, ey = math.cos(a) * r * 1.55, math.sin(a) * r * 1.55
            c.drawLine(math.cos(a) * r * 0.8, math.sin(a) * r * 0.8, ex, ey, crown)
            c.drawLine(ex, ey, ex + math.cos(a + 0.9) * r * 0.32, ey + math.sin(a + 0.9) * r * 0.32, crown)
            c.drawLine(ex, ey, ex + math.cos(a - 0.9) * r * 0.32, ey + math.sin(a - 0.9) * r * 0.32, crown)
        # body with soft blue shading + outline
        c.drawCircle(0, 0, r, skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
            (-r * 0.35, -r * 0.4), r * 1.5, [hex2color("#FFFFFF"), hex2color("#EAF5FF"), hex2color("#A9D3FF")], [0, 0.5, 1])))
        c.drawCircle(0, 0, r, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2.2,
                                         Color=hex2color("#5E8FD6")))
        # cheeks
        cheek = skia.Paint(AntiAlias=True, Color=hex2color("#FF9DB8", 170))
        c.drawOval(skia.Rect(-r * 0.72, r * 0.08, -r * 0.38, r * 0.3), cheek)
        c.drawOval(skia.Rect(r * 0.38, r * 0.08, r * 0.72, r * 0.3), cheek)
        ink = skia.Paint(AntiAlias=True, Color=hex2color("#1D2A4A"))
        blink = (math.sin(t * 1.3 + seed * 3) > 0.985) and not scared
        if scared:
            # wide eyes + "O" mouth
            for ex in (-r * 0.33, r * 0.33):
                c.drawCircle(ex, -r * 0.12, r * 0.2, skia.Paint(AntiAlias=True, Color=hex2color("#FFFFFF")))
                c.drawCircle(ex, -r * 0.12, r * 0.2, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                                               StrokeWidth=1.6, Color=hex2color("#1D2A4A")))
                c.drawCircle(ex, -r * 0.08, r * 0.09, ink)
            c.drawOval(skia.Rect(-r * 0.14, r * 0.22, r * 0.14, r * 0.58), ink)
            # sweat drop
            d = skia.Path()
            d.moveTo(r * 0.78, -r * 0.62); d.quadTo(r * 1.02, -r * 0.2, r * 0.8, -r * 0.18)
            d.quadTo(r * 0.6, -r * 0.2, r * 0.78, -r * 0.62)
            c.drawPath(d, skia.Paint(AntiAlias=True, Color=hex2color("#7CC4FF")))
        else:
            for ex in (-r * 0.32, r * 0.32):
                if blink:
                    c.drawLine(ex - r * 0.12, -r * 0.1, ex + r * 0.12, -r * 0.1,
                               skia.Paint(AntiAlias=True, StrokeWidth=2, Color=hex2color("#1D2A4A")))
                else:
                    c.drawCircle(ex, -r * 0.1, r * 0.13, ink)
                    c.drawCircle(ex + r * 0.04, -r * 0.15, r * 0.045, skia.Paint(AntiAlias=True, Color=hex2color("#FFFFFF")))
            # determined little smile
            m = skia.Path()
            m.moveTo(-r * 0.2, r * 0.25); m.quadTo(0, r * 0.45, r * 0.2, r * 0.25)
            c.drawPath(m, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2,
                                     StrokeCap=skia.Paint.kRound_Cap, Color=hex2color("#1D2A4A")))
        c.restore()

    def text(self, c, s, f, y, col, outline=False):
        w = f.measureText(s)
        x = W / 2 - w / 2
        c.drawString(s, x, y + 5, f, skia.Paint(AntiAlias=True, Color=skia.Color(0, 0, 0, 170),
                                                MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 7)))
        if outline:
            c.drawString(s, x, y, f, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=8,
                                                StrokeJoin=skia.Paint.kRound_Join, Color=skia.Color(40, 12, 6, 220)))
        c.drawString(s, x, y, f, skia.Paint(AntiAlias=True, Color=col))


def render_video(sim, out_path, audio_path=None):
    fps = sim["cfg"].fps
    r = VolcanoRenderer(sim)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}", "-r", str(fps), "-i", "-"]
    if audio_path:
        cmd += ["-i", audio_path, "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = skia.Surface(W, H)
    for fi in range(len(sim["frames"])):
        r.frame(fi, surf)
        proc.stdin.write(surf.makeImageSnapshot().toarray(colorType=skia.ColorType.kRGBA_8888_ColorType).tobytes())
    proc.stdin.close()
    proc.wait()


def render_stills(sim, frames, out_dir):
    r = VolcanoRenderer(sim)
    surf = skia.Surface(W, H)
    want = set(frames)
    for fi in range(max(frames) + 1):
        r.frame(fi, surf)
        if fi in want:
            surf.makeImageSnapshot().save(f"{out_dir}/volcano-{fi:05d}.png", skia.kPNG)
