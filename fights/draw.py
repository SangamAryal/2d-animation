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


def draw_sword(c, J, steel, dark, alpha=1.0, broken=0.0, kind="katana"):
    sx, sy = J["sw_dir"]
    hilt0 = J["hilt0"]
    guard = J["guard"]
    tip = J["tip"]
    if broken > 0.5:
        tip = (guard[0] + sx * 34 * J["size"], guard[1] + sy * 34 * J["size"])
    nx, ny = -sy * J["facing"], sx * J["facing"]
    if kind == "cleaver":
        # huge single-edged blade: wide spine, flat tip
        L = math.hypot(tip[0] - guard[0], tip[1] - guard[1])
        w0, w1 = 9.0 * J["size"], 13.0 * J["size"]
        p = skia.Path()
        p.moveTo(guard[0] + nx * w0 * 0.3, guard[1] + ny * w0 * 0.3)
        p.lineTo(tip[0] + nx * w1 * 0.3, tip[1] + ny * w1 * 0.3)
        p.lineTo(tip[0] - nx * w1 * 0.7 + sx * -6, tip[1] - ny * w1 * 0.7 + sy * -6)
        p.lineTo(guard[0] - nx * w0 * 0.7, guard[1] - ny * w0 * 0.7)
        p.close()
        c.drawPath(p, fill(col(steel, alpha)))
        c.drawPath(p, stroke(col(dark, alpha), 2.6))
        # dark spine
        c.drawLine(guard[0] + nx * w0 * 0.3, guard[1] + ny * w0 * 0.3,
                   tip[0] + nx * w1 * 0.3, tip[1] + ny * w1 * 0.3,
                   stroke(col(dark, alpha), 3.4))
    else:
        mid = ((guard[0] + tip[0]) / 2 + nx * 3.5, (guard[1] + tip[1]) / 2 + ny * 3.5)
        path = skia.Path()
        path.moveTo(*guard)
        path.quadTo(mid[0], mid[1], tip[0], tip[1])
        c.drawPath(path, stroke(col(dark, alpha), 5.2))
        c.drawPath(path, stroke(col(steel, alpha), 2.6))
    line(c, hilt0, guard, stroke(col(dark, alpha), 5.5 * J["size"], skia.Paint.kButt_Cap))
    g = 6 * J["size"]
    gx, gy = -sy * g, sx * g
    line(c, (guard[0] - gx, guard[1] - gy), (guard[0] + gx, guard[1] + gy),
         stroke(col("#c9a24a", alpha), 4.2 * J["size"]))


def draw_scabbard(c, J, color, steel, dark, sheathed, alpha=1.0):
    s0, s1 = J["sc0"], J["sc1"]
    line(c, s0, s1, stroke(col(color, alpha), 5.0))
    if sheathed:
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
    S = J["size"]
    rot = p.get("rot", 0)
    W = style.get("limb", LIMB_W) * S
    body = flat or style["body"]
    back = flat or style["back"]
    pb = stroke(col(back, alpha), W)
    pf = stroke(col(body, alpha), W)
    headless = p.get("headless", 0) > 0.5
    if tails and style.get("band") and not headless:
        polyline(c, tails[0], stroke(col(flat or style["band"], alpha), 3.6 * S))
        polyline(c, tails[1], stroke(col(flat or style["band"], alpha), 2.8 * S))
    polyline(c, [J["sho"], J["elb"], J["hab"]], pb)
    polyline(c, [J["hip"], J["knb"], J["ftb"]], pb)
    if style.get("scabbard"):
        draw_scabbard(c, J, flat or style["scab"], flat or style["steel"],
                      flat or "#222222", p["sheath"] > 0.5, alpha)
    line(c, J["hip"], J["neck"], stroke(col(body, alpha), W * style.get("torso", 1.0)))
    polyline(c, [J["hip"], J["knf"], J["ftf"]], pf)
    hx, hy = J["head"]
    R = R_HEAD * S * style.get("head", 1.0)
    if headless:
        # bloody stump at the neck
        c.drawCircle(J["neck"][0], J["neck"][1], W * 0.55, fill(col(flat or "#7a0a10", alpha)))
        style = dict(style, band=None, hat=None, horns=None, eye=None)
    else:
        c.drawCircle(hx, hy, R, fill(col(body, alpha)))
    a = p["H"] + rot
    ux, uy = d(a)
    ux *= J["facing"]
    rx, ry = d(a + 90)
    rx *= J["facing"]
    if style.get("band"):
        cx, cy = hx + ux * 3 * S, hy + uy * 3 * S
        line(c, (cx - rx * R, cy - ry * R), (cx + rx * R, cy + ry * R),
             stroke(col(flat or style["band"], alpha), 4.5 * S, skia.Paint.kButt_Cap))
    if style.get("hat"):
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
    if style.get("horns"):
        # helmet rim + two horns
        hc = flat or style["horns"]
        line(c, (hx - rx * R * 1.15 + ux * 2, hy - ry * R * 1.15 + uy * 2),
             (hx + rx * R * 1.15 + ux * 2, hy + ry * R * 1.15 + uy * 2),
             stroke(col(hc, alpha), 4.5 * S))
        for side in (-1, 1):
            b = (hx + rx * R * 0.8 * side + ux * R * 0.4, hy + ry * R * 0.8 * side + uy * R * 0.4)
            m = (b[0] + rx * 9 * S * side + ux * 9 * S, b[1] + ry * 9 * S * side + uy * 9 * S)
            t = (m[0] + ux * 9 * S - rx * 2 * S * side, m[1] + uy * 9 * S - ry * 2 * S * side)
            polyline(c, [b, m, t], stroke(col(hc, alpha), 4.0 * S))
    if style.get("eye"):
        ex, ey = hx + J["facing"] * 0 + (d(a + 90)[0] * J["facing"]) * R * 0.45 + ux * R * 0.15, \
            hy + d(a + 90)[1] * R * 0.45 + uy * R * 0.15
        c.drawCircle(ex, ey, 2.2 * S, fill(col(flat or style["eye"], alpha)))
    if p["sheath"] < 0.5 and not style.get("unarmed"):
        draw_sword(c, J, flat or style["steel"], flat or "#222222", alpha,
                   p.get("broken", 0), style.get("sword", "katana"))
    polyline(c, [J["sho"], J["elf"], J["haf"]], pf)
