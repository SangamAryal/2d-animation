"""Shorts thumbnail (1080x1920) for fight 03 "FIRE vs ICE".

python3 fights/tools/thumb_fire.py OUT.png
"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import skia  # noqa: E402

from draw import col, fill, stroke  # noqa: E402
from render import FPS, Renderer, typeface  # noqa: E402


def main(out, vt=6.78, zoom=1.3):
    r = Renderer(fight="fire")
    r.overlay_text = lambda c, v: None
    i = int(vt * FPS)
    cx, z = r.cams[i]
    r.cams[i] = (cx, z * zoom)
    r.gy = r.H * 0.66
    surf = skia.Surface(r.W, r.H)
    c = surf.getCanvas()
    r.render_frame(c, i)
    W, H = r.W, r.H
    # dark gradient at the top so the text pops
    p = skia.Paint()
    p.setShader(skia.GradientShader.MakeLinear(
        [(0, 0), (0, H * 0.42)], [col("#120d0a", 0.75).toColor(), col("#120d0a", 0.0).toColor()]))
    c.drawRect(skia.Rect(0, 0, W, H * 0.42), p)

    def text(s, x, y, size, color, align=0.5, outline=14):
        f = skia.Font(typeface("ExtraBold"), size)
        w = f.measureText(s)
        x0 = x - w * align
        c.drawString(s, x0 + 8, y + 10, f, fill(col("#000000", 0.45)))
        c.drawString(s, x0, y, f, stroke(col("#1b1714"), outline))
        c.drawString(s, x0, y, f, fill(col(color)))
    text("FIRE", W * 0.06, 330, 250, "#ff5a1f", align=0)
    text("VS", W * 0.5, 470, 130, "#ffffff")
    text("ICE", W * 0.94, 640, 250, "#5cc8ff", align=1)
    text("WHO WINS?", W / 2, H * 0.86, 140, "#ffd23f")
    surf.makeImageSnapshot().save(out)


if __name__ == "__main__":
    main(sys.argv[1])
