"""Draws the simulation frames with Skia and pipes them to ffmpeg."""
from __future__ import annotations

import math
import subprocess
from pathlib import Path

import numpy as np
import skia

HERE = Path(__file__).parent
W, H = 1080, 1920
CX, CY = 540, 1010

# Generation colours: our own neon run, one per split generation.
PALETTE = [
    "#FF4D5E", "#FF8A3D", "#FFC93C", "#C6F43A", "#4DF08A", "#2EE6C9",
    "#38C6FF", "#4D7CFF", "#8B5CFF", "#D14DFF", "#FF4DB8", "#7CFFCB",
    "#FF4D5E", "#FF8A3D",
]


def hex2color(h: str, a: int = 255) -> int:
    h = h.lstrip("#")
    return skia.Color(int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def font(name: str, size: float) -> skia.Font:
    tf = skia.Typeface.MakeFromFile(str(HERE / "fonts" / name))
    f = skia.Font(tf, size)
    f.setEdging(skia.Font.Edging.kAntiAlias)
    return f


def make_background(ring_r: float, accent: str = "#9B7BFF") -> skia.Image:
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    c.clear(hex2color("#07070D"))
    p = skia.Paint(Shader=skia.GradientShader.MakeRadial(
        (CX, CY), 900, [hex2color("#1A1030"), hex2color("#0C0A18"), hex2color("#05050A")], [0, 0.55, 1]))
    c.drawRect(skia.Rect(0, 0, W, H), p)
    # inner arena tint
    p = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
        (CX, CY), ring_r, [hex2color("#1E1236"), hex2color("#120C22")], [0, 1]))
    c.drawCircle(CX, CY, ring_r, p)
    # ring glow + ring
    for width, alpha, blur in [(26, 70, 18), (10, 140, 6)]:
        g = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=width,
                       Color=hex2color(accent, alpha),
                       MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur))
        c.drawCircle(CX, CY, ring_r + 4, g)
    ring = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=5,
                      Color=hex2color("#EDE6FF"))
    c.drawCircle(CX, CY, ring_r + 4, ring)
    # faint tick marks around the ring, like a dial
    tick = skia.Paint(AntiAlias=True, StrokeWidth=3, Color=hex2color("#EDE6FF", 70))
    for k in range(60):
        a = k / 60 * 2 * math.pi
        r0 = ring_r + 18 + (8 if k % 5 == 0 else 0)
        r1 = ring_r + 30
        c.drawLine(CX + r0 * math.cos(a), CY + r0 * math.sin(a), CX + r1 * math.cos(a), CY + r1 * math.sin(a), tick)
    return surf.makeImageSnapshot()


def blade_path(length: float, hw: float, hilt: float) -> tuple:
    """Katana in local coords: pivot at origin, blade along +x, gentle upward curve."""
    curve = 10.0
    def cy(x):  # curve offset of the spine
        u = x / length
        return -curve * u * u
    blade = skia.Path()
    xs = np.linspace(14, length - 36, 24)
    blade.moveTo(14, -hw + cy(14))
    for x in xs:
        blade.lineTo(x, -hw + cy(x))
    blade.lineTo(length, cy(length) - hw * 0.3)          # kissaki tip
    blade.lineTo(length - 30, hw * 0.9 + cy(length - 30))
    for x in xs[::-1]:
        blade.lineTo(x, hw + cy(x))
    blade.close()
    edge = skia.Path()  # bright cutting-edge line
    edge.moveTo(14, hw * 0.55 + cy(14))
    for x in xs:
        edge.lineTo(x, hw * 0.55 + cy(x))
    edge.lineTo(length - 2, cy(length) - hw * 0.2)
    handle = skia.Path()
    handle.addRRect(skia.RRect.MakeRectXY(skia.Rect(-hilt, -7, -6, 7), 5, 5))
    return blade, edge, handle


def shuriken_path(length: float, points: int) -> skia.Path:
    """Throwing star: `points` curved blades around a hub, tips at `length`."""
    p = skia.Path()
    inner = length * 0.28
    for k in range(points):
        a = k * 2 * math.pi / points
        a_prev = a - math.pi / points
        tip = (length * math.cos(a), length * math.sin(a))
        valley = (inner * math.cos(a_prev), inner * math.sin(a_prev))
        ctrl = (length * 0.55 * math.cos(a - 0.35), length * 0.55 * math.sin(a - 0.35))
        if k == 0:
            p.moveTo(*valley)
        else:
            p.lineTo(*valley)
        p.quadTo(ctrl[0], ctrl[1], tip[0], tip[1])
        valley2 = (inner * math.cos(a + math.pi / points), inner * math.sin(a + math.pi / points))
        p.lineTo(*valley2)
    p.close()
    return p


class Renderer:
    def __init__(self, sim: dict, scenario):
        self.sim = sim
        self.sc = scenario
        cfg = sim["cfg"]
        self.cfg = cfg
        self.bg = make_background(cfg.ring_radius, scenario.accent)
        if scenario.cutter == "katana":
            b = cfg.blades[0]
            self.blade, self.edge, self.handle = blade_path(b[2], cfg.blade_half_width + 1.5, -b[1])
            self.hilt_length = -b[1]
        if scenario.cutter == "shuriken":
            self.star = shuriken_path(cfg.blades[0][2], len(cfg.blades))
        self.title = scenario.title
        self.f_title = font("InterDisplay-Black.otf", 150 if len(self.title) <= 8 else 124)
        self.f_count = font("InterDisplay-Black.otf", 120)
        self.f_label = font("InterDisplay-Bold.otf", 38)
        self.f_small = font("InterDisplay-Bold.otf", 34)
        self.colors = [hex2color(h) for h in (scenario.palette or PALETTE)]
        self.flashes = []  # (frame, x, y, gen)
        self.eat_glow = 0.0

    def draw_blade(self, c: skia.Canvas, angle: float, alpha: int, ghost: bool, pivot=(0.0, 0.0)):
        c.save()
        c.translate(CX + pivot[0], CY + pivot[1])
        c.rotate(math.degrees(angle))
        if ghost:
            c.drawPath(self.blade, skia.Paint(AntiAlias=True, Color=hex2color("#C9D6FF", alpha)))
        else:
            glow = skia.Paint(AntiAlias=True, Color=hex2color("#BFD0FF", 110),
                              MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 9))
            c.drawPath(self.blade, glow)
            steel = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeLinear(
                [(0, -8), (0, 8)], [hex2color("#8E97AE"), hex2color("#F4F7FF"), hex2color("#DDE4F5")], [0, 0.6, 1]))
            c.drawPath(self.blade, steel)
            c.drawPath(self.edge, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style,
                                             StrokeWidth=1.6, Color=hex2color("#FFFFFF")))
            # handle with wrap pattern
            c.drawPath(self.handle, skia.Paint(AntiAlias=True, Color=hex2color("#1A1020")))
            wrap = skia.Paint(AntiAlias=True, Color=hex2color("#E8344E"))
            hl = self.hilt_length
            x = -hl + 8
            while x < -16:
                d = skia.Path()
                d.moveTo(x, 0); d.lineTo(x + 6, -5.5); d.lineTo(x + 12, 0); d.lineTo(x + 6, 5.5); d.close()
                c.drawPath(d, wrap)
                x += 13
            c.drawRRect(skia.RRect.MakeRectXY(skia.Rect(-hl - 6, -8, -hl + 2, 8), 3, 3),
                        skia.Paint(AntiAlias=True, Color=hex2color("#C9A24A")))
            # tsuba (guard)
            c.drawOval(skia.Rect(-7, -15, 9, 15), skia.Paint(AntiAlias=True, Color=hex2color("#C9A24A")))
            c.drawOval(skia.Rect(-4, -10, 6, 10), skia.Paint(AntiAlias=True, Color=hex2color("#6B4E1C")))
        c.restore()

    def draw_shuriken(self, c, angle, alpha, ghost, pivot):
        c.save()
        c.translate(CX + pivot[0], CY + pivot[1])
        c.rotate(math.degrees(angle))
        if ghost:
            c.drawPath(self.star, skia.Paint(AntiAlias=True, Color=hex2color("#BFF6FF", alpha)))
        else:
            c.drawPath(self.star, skia.Paint(AntiAlias=True, Color=hex2color("#9FF3FF", 120),
                                             MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 12)))
            steel = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
                (0, 0), 150, [hex2color("#5E6678"), hex2color("#E9EEF8"), hex2color("#FFFFFF")], [0.1, 0.55, 1]))
            c.drawPath(self.star, steel)
            c.drawPath(self.star, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=2,
                                             Color=hex2color("#FFFFFF")))
            c.drawCircle(0, 0, 20, skia.Paint(AntiAlias=True, Color=hex2color("#12101E")))
            c.drawCircle(0, 0, 20, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=4,
                                              Color=hex2color(self.sc.accent)))
        c.restore()

    def draw_laser(self, c, angle, fi):
        L = self.cfg.blades[0][2]
        flick = 1.0 + 0.08 * math.sin(fi * 1.7) + 0.05 * math.sin(fi * 4.3)
        c.save()
        c.translate(CX, CY)
        c.rotate(math.degrees(angle))
        for w, a, blur in [(34 * flick, 70, 16), (14 * flick, 170, 6)]:
            c.drawLine(-L, 0, L, 0, skia.Paint(AntiAlias=True, StrokeWidth=w, Color=hex2color(self.sc.accent, a),
                                               StrokeCap=skia.Paint.kRound_Cap,
                                               MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, blur)))
        c.drawLine(-L, 0, L, 0, skia.Paint(AntiAlias=True, StrokeWidth=4, Color=hex2color("#FFFFFF"),
                                           StrokeCap=skia.Paint.kRound_Cap))
        # emitter hub
        c.drawCircle(0, 0, 26, skia.Paint(AntiAlias=True, Color=hex2color("#16121F")))
        c.drawCircle(0, 0, 26, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=5,
                                          Color=hex2color(self.sc.accent)))
        c.drawCircle(0, 0, 9, skia.Paint(AntiAlias=True, Color=hex2color("#FFFFFF")))
        c.restore()

    def draw_hole(self, c, radius, fi):
        if radius <= 0:
            return
        self.eat_glow = self.eat_glow * 0.9 + (0.6 if self.sim["eats"][fi] else 0.0)
        g = min(1.0, self.eat_glow)
        # accretion glow
        p = skia.Paint(AntiAlias=True, Shader=skia.GradientShader.MakeRadial(
            (CX, CY), radius * 2.6, [hex2color(self.sc.accent, int(200 + 55 * g)), hex2color("#FF4D6D", 90),
                                     hex2color("#000000", 0)], [0.35, 0.6, 1]))
        c.drawCircle(CX, CY, radius * 2.6, p)
        # swirling arcs
        c.save()
        c.translate(CX, CY)
        c.rotate(-fi * 4.0)
        arc = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3,
                         Color=hex2color("#FFE2B0", 160), StrokeCap=skia.Paint.kRound_Cap)
        for k in range(3):
            rr = radius * (1.25 + 0.25 * k)
            c.drawArc(skia.Rect(-rr, -rr, rr, rr), k * 120, 70, False, arc)
        c.restore()
        c.drawCircle(CX, CY, radius, skia.Paint(AntiAlias=True, Color=hex2color("#000000")))
        c.drawCircle(CX, CY, radius, skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3,
                                                Color=hex2color("#FFD9A0", 220)))

    def draw_wedge(self, c, ang, om):
        sweep_deg = max(10.0, min(60.0, abs(om) * 4.0))
        wedge = skia.Path()
        L = self.cfg.blades[0][2]
        wedge.moveTo(CX, CY)
        wedge.arcTo(skia.Rect(CX - L, CY - L, CX + L, CY + L), math.degrees(ang), sweep_deg, False)
        wedge.close()
        shader = skia.GradientShader.MakeSweep(CX, CY, [hex2color("#C9D6FF", 70), hex2color("#C9D6FF", 0)],
                                               [0.0, sweep_deg / 360.0],
                                               localMatrix=skia.Matrix.RotateDeg(math.degrees(ang), (CX, CY)))
        c.drawPath(wedge, skia.Paint(AntiAlias=True, Shader=shader))


    def draw_text_center(self, c, text, f, y, color, shadow=True):
        w = f.measureText(text)
        if shadow:
            c.drawString(text, CX - w / 2, y + 6, f, skia.Paint(AntiAlias=True, Color=hex2color("#000000", 150),
                         MaskFilter=skia.MaskFilter.MakeBlur(skia.kNormal_BlurStyle, 8)))
        c.drawString(text, CX - w / 2, y, f, skia.Paint(AntiAlias=True, Color=color))

    def frame(self, fi: int, surf: skia.Surface):
        c = surf.getCanvas()
        c.drawImage(self.bg, 0, 0)
        sim = self.sim
        r = self.cfg.ball_radius
        n_frames = len(sim["pos"])

        # title + subtitle
        self.draw_text_center(c, self.title, self.f_title, 330, hex2color("#FFFFFF"))
        self.draw_text_center(c, self.sc.subtitle, self.f_label, 400, hex2color("#B9A8FF"), shadow=False)

        ang = sim["angle"][fi]
        om = sim["omega"][fi]
        pivot = sim["pivot"][fi]
        self.draw_hole(c, sim["hole"][fi], fi)
        if self.sc.cutter == "katana":
            self.draw_wedge(c, ang, om)

        # balls, batched by colour
        pos = sim["pos"][fi]
        gen = sim["gen"][fi]
        if len(pos):
            for g in np.unique(gen):
                path = skia.Path()
                sel = pos[gen == g]
                for (x, y) in sel:
                    path.addCircle(CX + float(x), CY + float(y), r)
                c.drawPath(path, skia.Paint(AntiAlias=True, Color=self.colors[int(g) % len(self.colors)]))
            hi = skia.Path()
            for (x, y) in pos:
                hi.addCircle(CX + float(x) - r * 0.32, CY + float(y) - r * 0.32, r * 0.32)
            c.drawPath(hi, skia.Paint(AntiAlias=True, Color=hex2color("#FFFFFF", 90)))

        # cut flashes
        for (x, y, g) in sim["cuts"][fi]:
            self.flashes.append((fi, x, y, g))
        self.flashes = [fl for fl in self.flashes if fi - fl[0] < 14][-120:]
        for (f0, x, y, g) in self.flashes:
            k = (fi - f0) / 14.0
            a = int(220 * (1 - k))
            col = self.colors[int(g) % len(self.colors)]
            p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style, StrokeWidth=3 * (1 - k) + 0.5,
                           Color=skia.ColorSetA(col, a))
            c.drawCircle(CX + x, CY + y, r + 26 * k, p)

        # cutter: ghosts then the real thing
        ghosts = [(3, 30), (2, 55), (1, 90)]
        if self.sc.cutter == "katana":
            for k, a in ghosts:
                if fi - k >= 0:
                    self.draw_blade(c, sim["angle"][fi - k], a, True, sim["pivot"][fi - k])
            self.draw_blade(c, ang, 255, False, pivot)
        elif self.sc.cutter == "shuriken":
            for k, a in ghosts:
                if fi - k >= 0:
                    self.draw_shuriken(c, sim["angle"][fi - k], a, True, sim["pivot"][fi - k])
            self.draw_shuriken(c, ang, 255, False, pivot)
        elif self.sc.cutter == "laser":
            self.draw_laser(c, ang, fi)

        # counter
        n = len(pos)
        full = sim["full_frame"] is not None and fi >= sim["full_frame"]
        col = hex2color("#FFD45C") if full else hex2color("#FFFFFF")
        txt = f"{n:,}"
        scale = 1.0
        if sim["cuts"][fi] or (fi > 0 and sim["cuts"][fi - 1]):
            scale = 1.06
        c.save()
        c.translate(CX, 1640)
        c.scale(scale, scale)
        c.translate(-CX, -1640)
        self.draw_text_center(c, txt, self.f_count, 1680, col)
        c.restore()
        end_label = self.sc.end_text.get(sim["end_kind"], "")
        self.draw_text_center(c, end_label if full else "BALLS", self.f_label, 1745,
                              hex2color("#FFD45C") if full else hex2color("#8C84A8"), shadow=False)
        if self.cfg.hole_radius > 0:
            self.draw_text_center(c, f"SWALLOWED  {sim['eaten'][fi]:,}", self.f_small, 1810,
                                  hex2color("#FFB347"), shadow=False)

        # fade in / out
        fade = 1.0
        if fi < 12:
            fade = fi / 12
        if fi > n_frames - 30:
            fade = max(0.0, (n_frames - fi) / 30)
        if fade < 1:
            c.drawRect(skia.Rect(0, 0, W, H), skia.Paint(Color=skia.Color(0, 0, 0, int(255 * (1 - fade)))))


def render_video(sim: dict, scenario, out_path: str, audio_path: str | None = None,
                 frames: range | None = None):
    fps = sim["cfg"].fps
    rend = Renderer(sim, scenario)
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{W}x{H}",
           "-r", str(fps), "-i", "-"]
    if audio_path:
        cmd += ["-i", audio_path, "-c:a", "aac", "-b:a", "192k", "-shortest"]
    cmd += ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
            "-movflags", "+faststart", out_path]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    surf = skia.Surface(W, H)
    rng = frames or range(len(sim["pos"]))
    for fi in rng:
        rend.frame(fi, surf)
        img = surf.makeImageSnapshot()
        # convert explicitly: the surface's native byte order varies by platform
        proc.stdin.write(img.toarray(colorType=skia.ColorType.kRGBA_8888_ColorType).tobytes())
    proc.stdin.close()
    proc.wait()


def render_still(sim: dict, scenario, fi: int, out_png: str):
    rend = Renderer(sim, scenario)
    surf = skia.Surface(W, H)
    for k in range(max(0, fi - 14), fi + 1):  # warm up flashes
        rend.frame(k, surf)
    surf.makeImageSnapshot().save(out_png, skia.kPNG)
