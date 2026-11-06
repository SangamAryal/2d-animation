"""Render every pose in a grid: python3 fights/tools/pose_sheet.py out.png"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import skia
from rig import P, solve
from draw import draw_fighter, col
from styles import RONIN, KASA

names = list(P)
cols = 6
W, H = 260, 300
rows = (len(names) + cols - 1) // cols
surf = skia.Surface(cols * W, rows * H)
c = surf.getCanvas()
c.clear(col("#f4efe6"))
font = skia.Font(skia.Typeface("DejaVu Sans"), 16)
for i, n in enumerate(names):
    gx, gy = (i % cols) * W, (i // cols) * H
    c.save()
    c.translate(gx + W / 2, gy + H - 40)
    c.scale(1, -1)
    c.drawLine(-120, 0, 120, 0, skia.Paint(Color=skia.ColorGRAY))
    J = solve(P[n], 0, 1)
    draw_fighter(c, J, RONIN if i % 2 == 0 else KASA)
    c.restore()
    c.drawString(n, gx + 10, gy + H - 12, font, skia.Paint(Color=skia.ColorBLACK))
surf.makeImageSnapshot().save(sys.argv[1])
