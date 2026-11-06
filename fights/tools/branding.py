"""Channel art for "Stick Clash": profile 800x800 and banner 2560x1440.

python3 fights/tools/branding.py OUT_DIR
"""
import math
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import numpy as np  # noqa: E402
import skia  # noqa: E402

from choreo_power import POWER, SPEED  # noqa: E402
from draw import col, draw_fighter, fill, stroke  # noqa: E402
from render import typeface  # noqa: E402
from rig import P, solve  # noqa: E402


def fighter(c, who, pose, x, facing, **over):
    st = SPEED if who == "S" else POWER
    p = dict(P[pose])
    p.update(over)
    J = solve(p, x, facing, size=st["size"], blade=st["blade"])
    tails = None
    if st.get("band"):
        hx, hy = J["head"]
        b = (hx - facing * 10 * st["size"], hy + 3)
        tails = ([(b[0] - facing * k * 9, b[1] - k * 1.5 + math.sin(k) * 4) for k in range(9)],
                 [(b[0] - facing * k * 8, b[1] - k * 4 - math.sin(k) * 3) for k in range(9)])
    # motion ghosts for SPEED
    if who == "S":
        for k in range(1, 5):
            Jg = solve(p, x - facing * k * 16, facing, size=st["size"], blade=st["blade"])
            draw_fighter(c, Jg, st, alpha=0.3 * (1 - k / 5), flat=st["ghost"])
    draw_fighter(c, J, st, tails=tails)
    return J


def clash_star(c, x, y, r, n=10, seed=3):
    rng = np.random.default_rng(seed)
    for i in range(26):
        a = rng.uniform(0, 2 * math.pi)
        r0, r1 = r * rng.uniform(0.6, 1.0), r * rng.uniform(1.4, 2.6)
        c.drawLine(x + math.cos(a) * r0, y + math.sin(a) * r0,
                   x + math.cos(a) * r1, y + math.sin(a) * r1,
                   stroke(col("#ffd36b", 0.9), rng.uniform(2, 4)))
    path = skia.Path()
    for i in range(2 * n):
        rr = r if i % 2 == 0 else r * 0.3
        a = i / (2 * n) * 2 * math.pi + 0.2
        px, py = x + math.cos(a) * rr, y + math.sin(a) * rr
        path.moveTo(px, py) if i == 0 else path.lineTo(px, py)
    path.close()
    c.drawPath(path, fill(col("#ffffff")))
    c.drawPath(path, stroke(col("#ffcf5a"), 3))


def background(c, W, H, gy, sun=True, sun_x=None):
    sky = skia.Paint()
    sky.setShader(skia.GradientShader.MakeLinear(
        [(0, 0), (0, gy)], [col("#eadfcb").toColor(), col("#f7f2e9").toColor()]))
    c.drawRect(skia.Rect(0, 0, W, gy), sky)
    if sun:
        c.drawCircle(sun_x or W / 2, gy - H * 0.30, min(W, H) * 0.30, fill(col("#e6a48f", 0.45)))
    path = skia.Path()
    path.moveTo(0, gy)
    for i in range(0, W + 20, 20):
        h = 40 + 25 * math.sin(i * 0.004) + 15 * math.sin(i * 0.011 + 1) + 8 * math.sin(i * 0.031)
        path.lineTo(i, gy - h * H / 1440 * 1.6)
    path.lineTo(W, gy)
    path.close()
    c.drawPath(path, fill(col("#d9c9b0", 0.8)))
    fl = skia.Paint()
    fl.setShader(skia.GradientShader.MakeLinear(
        [(0, gy), (0, H)], [col("#e2d5bf").toColor(), col("#cdbb9f").toColor()]))
    c.drawRect(skia.Rect(0, gy, W, H), fl)
    for k in range(-12, 13):
        sx = W / 2 + k * W / 14
        c.drawLine(sx, gy, W / 2 + (sx - W / 2) * 3.2, H, stroke(col("#b9a585", 0.5), 2))
    c.drawLine(0, gy, W, gy, stroke(col("#2a2622"), 4))


def logo_text(c, x, y, size, center=True):
    f = skia.Font(typeface("ExtraBold"), size)
    a, b = "STICK ", "CLASH"
    wa, wb = f.measureText(a), f.measureText(b)
    x0 = x - (wa + wb) / 2 if center else x
    sh = fill(col("#1b1714", 0.35))
    c.drawString(a, x0 + size * 0.04, y + size * 0.05, f, sh)
    c.drawString(b, x0 + wa + size * 0.04, y + size * 0.05, f, sh)
    c.drawString(a, x0, y, f, fill(col(SPEED["body"])))
    c.drawString(b, x0 + wa, y, f, fill(col(POWER["body"])))


def clash_scene(c, cx, gy, z):
    """SPEED and POWER locked blade-to-blade around world x = 0."""
    c.save()
    c.translate(cx, gy)
    c.scale(z, -z)
    c.drawOval(skia.Rect(-210, -6, -110, 6), fill(col("#3a2e22", 0.25)))
    c.drawOval(skia.Rect(60, -7, 200, 7), fill(col("#3a2e22", 0.25)))
    Jp = fighter(c, "P", "high_cut", 135, -1, sw=118, uaf=110, faf=118, T=22)
    Js = fighter(c, "S", "block_high", -150, 1, sw=70, uaf=70, faf=20, T=10)
    # the meeting point of the two blades
    mx = (Jp["tip"][0] * 0.35 + Jp["guard"][0] * 0.65 + Js["tip"][0] * 0.5 + Js["guard"][0] * 0.5) / 2
    my = (Jp["tip"][1] * 0.35 + Jp["guard"][1] * 0.65 + Js["tip"][1] * 0.5 + Js["guard"][1] * 0.5) / 2
    clash_star(c, mx, my, 26)
    c.restore()


def profile(out):
    W = H = 800
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    gy = H * 0.70
    background(c, W, H, gy, sun=False)
    c.drawCircle(W / 2, H * 0.42, 260, fill(col("#e6a48f", 0.5)))
    clash_scene(c, W / 2 + 10, gy, 1.65)
    # name band at the bottom (stays inside the round crop)
    f = skia.Font(typeface("ExtraBold"), 74)
    t = "STICK CLASH"
    w = f.measureText(t)
    c.drawRoundRect(skia.Rect(W / 2 - w / 2 - 26, 585, W / 2 + w / 2 + 26, 675), 20, 20,
                    fill(col("#1b1714", 0.88)))
    fa = skia.Font(typeface("ExtraBold"), 74)
    wa = fa.measureText("STICK ")
    x0 = W / 2 - w / 2
    c.drawString("STICK ", x0, 655, fa, fill(col("#6db4e6")))
    c.drawString("CLASH", x0 + wa, 655, fa, fill(col("#ff5a5f")))
    surf.makeImageSnapshot().save(out)


def banner(out):
    W, H = 2560, 1440
    surf = skia.Surface(W, H)
    c = surf.getCanvas()
    gy = 920
    background(c, W, H, gy, sun_x=1640)
    FX = 1640   # fighters' centre, right half of the safe area
    rng = np.random.default_rng(5)
    for i in range(16):
        y = gy - rng.uniform(40, 280)
        x0 = FX - rng.uniform(220, 270)
        c.drawLine(x0, y, x0 - rng.uniform(90, 200), y,
                   stroke(col("#5fc2ff", 0.5), rng.uniform(2, 5)))
    for i in range(10):
        x, y = FX + 110, gy + 2
        path = skia.Path()
        path.moveTo(x, y)
        for j in range(5):
            x += rng.uniform(25, 60)
            y += rng.uniform(2, 12)
            path.lineTo(x, y)
        c.drawPath(path, stroke(col("#3a3128", 0.8), 3))
    clash_scene(c, FX, gy, 1.2)
    # logo stacked on the left of the safe area
    f = skia.Font(typeface("ExtraBold"), 168)
    lx = 560
    for txt, color, y in (("STICK", SPEED["body"], 690), ("CLASH", POWER["body"], 850)):
        c.drawString(txt, lx + 7, y + 8, f, fill(col("#1b1714", 0.35)))
        c.drawString(txt, lx, y, f, fill(col(color)))
    sub = skia.Font(typeface("Bold"), 38)
    c.drawString("STICK FIGHTS  •  NEW BATTLES WEEKLY", lx + 6, 905, sub,
                 fill(col("#5b4a39")))
    surf.makeImageSnapshot().save(out)


if __name__ == "__main__":
    d = sys.argv[1]
    os.makedirs(d, exist_ok=True)
    profile(os.path.join(d, "stick-clash-profile.png"))
    banner(os.path.join(d, "stick-clash-banner.png"))
    print("ok")
