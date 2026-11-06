"""Skia drawing for fighters, swords and effects (world coords, y up)."""
import math
import skia

from rig import R_HEAD, d

LIMB_W = 8.5


def col(hexs, a=1.0):
    hexs = hexs.lstrip("#")
    r, g, b = int(hexs[0:2], 16), int(hexs[2:4], 16), int(hexs[4:6], 16)
    return skia.Color4f(r / 255, g / 255, b / 255, a)


def stroke(color, w, cap=skia.Paint.kRound_Cap):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kStroke_Style,
                   StrokeWidth=w, StrokeCap=cap,
                   StrokeJoin=skia.Paint.kRound_Join)
    p.setColor4f(color)
    return p


def fill(color):
    p = skia.Paint(AntiAlias=True, Style=skia.Paint.kFill_Style)
    p.setColor4f(color)
    return p


def line(c, a, b, paint):
    c.drawLine(a[0], a[1], b[0], b[1], paint)


def polyline(c, pts, paint):
    path = skia.Path()
    path.moveTo(*pts[0])
    for q in pts[1:]:
        path.lineTo(*q)
    c.drawPath(path, paint)


def draw_sword(c, J, steel, dark, alpha=1.0, broken=0.0):
    hand = J["haf"]
    sx, sy = J["sw_dir"]
    hilt0 = J["hilt0"]
    guard = J["guard"]
    tip = J["tip"]
    if broken > 0.5:
        tip = (guard[0] + sx * 34, guard[1] + sy * 34)
    # blade with a slight curve (outline + steel core)
    nx, ny = -sy * J["facing"], sx * J["facing"]
    mid = ((guard[0] + tip[0]) / 2 + nx * 3.5, (guard[1] + tip[1]) / 2 + ny * 3.5)
    path = skia.Path()
    path.moveTo(*guard)
    path.quadTo(mid[0], mid[1], tip[0], tip[1])
    c.drawPath(path, stroke(col(dark, alpha), 5.2))
    c.drawPath(path, stroke(col(steel, alpha), 2.6))
    # hilt and guard
    line(c, hilt0, guard, stroke(col(dark, alpha), 5.5, skia.Paint.kButt_Cap))
    gx, gy = -sy * 6, sx * 6
    line(c, (guard[0] - gx, guard[1] - gy), (guard[0] + gx, guard[1] + gy),
         stroke(col("#c9a24a", alpha), 4.2))


def draw_scabbard(c, J, color, steel, dark, sheathed, alpha=1.0):
    s0, s1 = J["sc0"], J["sc1"]
    line(c, s0, s1, stroke(col(color, alpha), 5.0))
    if sheathed:
        # hilt sticking out forward of the scabbard mouth
        a = J["sc_a"] + 180
        sx, sy = d(a)
        sx *= J["facing"]
        h1 = (s0[0] + sx * 18, s0[1] + sy * 18)
        line(c, s0, h1, stroke(col(dark, alpha), 5.5, skia.Paint.kButt_Cap))
        gx, gy = -sy * 6, sx * 6
        line(c, (s0[0] - gx, s0[1] - gy), (s0[0] + gx, s0[1] + gy),
             stroke(col("#c9a24a", alpha), 4.2))


def draw_fighter(c, J, style, alpha=1.0, flat=None, tails=None):
    """flat: draw everything in one color (impact frames / afterimages)."""
    p = J["p"]
    body = flat or style["body"]
    back = flat or style["back"]
    pb = stroke(col(back, alpha), LIMB_W)
    pf = stroke(col(body, alpha), LIMB_W)
    # headband tails behind everything
    if tails and style.get("band"):
        polyline(c, tails[0], stroke(col(flat or style["band"], alpha), 3.4))
        polyline(c, tails[1], stroke(col(flat or style["band"], alpha), 2.6))
    polyline(c, [J["sho"], J["elb"], J["hab"]], pb)
    polyline(c, [J["hip"], J["knb"], J["ftb"]], pb)
    if style.get("scabbard"):
        draw_scabbard(c, J, flat or style["scab"], flat or style["steel"],
                      flat or "#222222", p["sheath"] > 0.5, alpha)
    line(c, J["hip"], J["neck"], pf)
    polyline(c, [J["hip"], J["knf"], J["ftf"]], pf)
    hx, hy = J["head"]
    c.drawCircle(hx, hy, R_HEAD, fill(col(body, alpha)))
    if style.get("band"):
        # headband across the forehead
        a = p["H"]
        sx, sy = d(a)
        sx *= J["facing"]
        cx, cy = hx + sx * 3, hy + sy * 3
        nx, ny = sy * J["facing"] * 0 + d(a + 90)[0] * J["facing"], d(a + 90)[1]
        line(c, (cx - nx * 12.5, cy - ny * 12.5), (cx + nx * 12.5, cy + ny * 12.5),
             stroke(col(flat or style["band"], alpha), 4.5, skia.Paint.kButt_Cap))
    if style.get("hat"):
        a = p["H"]
        ux, uy = d(a)
        ux *= J["facing"]
        rx, ry = d(a + 90)
        rx *= J["facing"]
        top = (hx + ux * 26, hy + uy * 26)
        b0 = (hx + ux * 5 - rx * 30, hy + uy * 5 - ry * 30)
        b1 = (hx + ux * 5 + rx * 30, hy + uy * 5 + ry * 30)
        path = skia.Path()
        path.moveTo(*top)
        path.lineTo(*b0)
        path.lineTo(*b1)
        path.close()
        c.drawPath(path, fill(col(flat or style["hat"], alpha)))
        c.drawPath(path, stroke(col(flat or style["body"], alpha), 2.0))
    if p["sheath"] < 0.5:
        draw_sword(c, J, flat or style["steel"], flat or "#222222", alpha,
                   p.get("broken", 0))
    polyline(c, [J["sho"], J["elf"], J["haf"]], pf)
