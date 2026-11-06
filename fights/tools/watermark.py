"""YouTube branding watermark (transparent PNG, 300x300): python3 watermark.py OUT_DIR"""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import skia
from draw import col, fill, stroke
from render import typeface

def blade(c, x0, y0, ang, L, w, color, edge="#1b1714", cleaver=False):
    ux, uy = math.cos(ang), math.sin(ang)
    nx, ny = -uy, ux
    hx, hy = x0 - ux * 30, y0 - uy * 30
    c.drawLine(hx, hy, x0, y0, stroke(col("#2a1f18"), 16))           # hilt
    c.drawLine(x0 - nx * 20, y0 - ny * 20, x0 + nx * 20, y0 + ny * 20,
               stroke(col("#e0b04a"), 12))                            # guard
    p = skia.Path()
    tw = w * (1.4 if cleaver else 0.15)
    p.moveTo(x0 + nx * w / 2, y0 + ny * w / 2)
    p.lineTo(x0 + ux * L + nx * tw / 2, y0 + uy * L + ny * tw / 2)
    p.lineTo(x0 + ux * (L + (0 if cleaver else 14)) - nx * tw / 2, y0 + uy * (L + (0 if cleaver else 14)) - ny * tw / 2)
    p.lineTo(x0 - nx * w / 2, y0 - ny * w / 2)
    p.close()
    c.drawPath(p, fill(col(color)))
    c.drawPath(p, stroke(col(edge), 4))

def make(out, label):
    S = 300
    surf = skia.Surface(S, S)
    c = surf.getCanvas()
    c.clear(skia.Color4f(0, 0, 0, 0))
    cx, cy, r = S / 2, S / 2, 140
    c.drawCircle(cx, cy, r, fill(col("#1b1714", 0.92)))
    c.drawCircle(cx, cy, r - 6, stroke(col("#ffffff"), 7))
    up = -22 if label else -4
    blade(c, cx + 62, cy + 62 + up, -3 * math.pi / 4, 160, 24, "#e2474f", cleaver=True)
    blade(c, cx - 62, cy + 62 + up, -math.pi / 4, 165, 13, "#cfe6f5")
    # spark where they cross
    sp = skia.Path()
    for i in range(16):
        rr = 26 if i % 2 == 0 else 8
        a = i / 16 * 2 * math.pi
        x, y = cx + math.cos(a) * rr, cy + up + math.sin(a) * rr
        sp.moveTo(x, y) if i == 0 else sp.lineTo(x, y)
    sp.close()
    c.drawPath(sp, fill(col("#ffd84a")))
    if label:
        f = skia.Font(typeface("ExtraBold"), 34)
        w = f.measureText(label)
        c.drawRoundRect(skia.Rect(cx - w / 2 - 14, 212, cx + w / 2 + 14, 256), 12, 12,
                        fill(col("#e2262f")))
        c.drawString(label, cx - w / 2, 246, f, fill(col("#ffffff")))
    surf.makeImageSnapshot().save(out)

d = sys.argv[1]
make(os.path.join(d, "watermark-subscribe.png"), "SUBSCRIBE")
make(os.path.join(d, "watermark-plain.png"), None)
print("ok")
