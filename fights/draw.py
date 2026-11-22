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


def limb(c, J, keys, paint):
    """Draw a limb chain. In drawn fights the bones are Bezier curves that
    bow with drag (J["bow"]) and the joint corners are rounded, so limbs read
    as brush strokes with an organic bend instead of rigid sticks."""
    bows = J.get("bow")
    if bows is None:
        polyline(c, [J[k] for k in keys], paint)
        return
    pts = [J[keys[0]]]
    for a, b in zip(keys[:-1], keys[1:]):
        p0, p1 = J[a], J[b]
        o = bows.get((a, b))
        if o is None:
            pts.append(p1)
            continue
        m = ((p0[0] + p1[0]) / 2 + o[0] * 2, (p0[1] + p1[1]) / 2 + o[1] * 2)
        for k in range(1, 7):
            u = k / 6
            pts.append(((1 - u) ** 2 * p0[0] + 2 * u * (1 - u) * m[0] + u * u * p1[0],
                        (1 - u) ** 2 * p0[1] + 2 * u * (1 - u) * m[1] + u * u * p1[1]))
    pr = skia.Paint(paint)
    pr.setPathEffect(skia.CornerPathEffect.Make(5.5 * J["size"]))
    polyline(c, pts, pr)


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
    elif kind == "longsword":
        # straight double-edged blade with a fuller and a point
        S = J["size"]
        L = math.hypot(tip[0] - guard[0], tip[1] - guard[1])
        ux, uy = (tip[0] - guard[0]) / L, (tip[1] - guard[1]) / L
        px, py = -uy, ux
        w = 3.6 * S
        base = (tip[0] - ux * 12 * S, tip[1] - uy * 12 * S)
        p = skia.Path()
        p.moveTo(guard[0] + px * w, guard[1] + py * w)
        p.lineTo(base[0] + px * w, base[1] + py * w)
        p.lineTo(*tip)
        p.lineTo(base[0] - px * w, base[1] - py * w)
        p.lineTo(guard[0] - px * w, guard[1] - py * w)
        p.close()
        c.drawPath(p, fill(col(steel, alpha)))
        c.drawPath(p, stroke(col(dark, alpha), 2.2 * S))
        line(c, guard, (base[0] - ux * 6 * S, base[1] - uy * 6 * S), stroke(col("#9aa6b0" if steel != dark else dark, alpha), 1.3 * S))
        line(c, hilt0, guard, stroke(col(dark, alpha), 5.5 * S, skia.Paint.kButt_Cap))
        c.drawCircle(hilt0[0], hilt0[1], 4.2 * S, fill(col(dark if steel == dark else "#c9a24a", alpha)))
        g = 13 * S
        gx, gy = -sy * g, sx * g
        line(c, (guard[0] - gx, guard[1] - gy), (guard[0] + gx, guard[1] + gy),
             stroke(col(dark if steel == dark else "#c9a24a", alpha), 4.6 * S))
        return
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


def draw_spear(c, J, style, alpha=1.0, flat=None, broken=0.0):
    """Long wooden shaft, leaf-shaped steel head, metal butt cap."""
    sx, sy = J["sw_dir"]
    S = J["size"]
    butt, tip, haf = J["hilt0"], J["tip"], J["haf"]
    L = math.hypot(tip[0] - haf[0], tip[1] - haf[1])
    ux, uy = (tip[0] - haf[0]) / L, (tip[1] - haf[1]) / L
    nx, ny = -uy, ux
    hl = style.get("head_len", 26) * S
    hb = (tip[0] - ux * hl, tip[1] - uy * hl)
    end = hb
    if broken > 0.5:
        cut = style.get("cut", 34) * S
        end = (haf[0] + ux * cut, haf[1] + uy * cut)
    dark = flat or "#1d1612"
    line(c, butt, end, stroke(col(dark, alpha), 6.4 * S))
    line(c, butt, end, stroke(col(flat or style.get("wood", "#8a5a33"), alpha), 3.6 * S))
    line(c, butt, (butt[0] + ux * 6 * S, butt[1] + uy * 6 * S),
         stroke(col(flat or "#c9a24a", alpha), 6.0 * S, skia.Paint.kButt_Cap))
    if broken > 0.5:
        # splintered end
        for k in (-1, 0, 1):
            line(c, end, (end[0] + ux * 5 * S + nx * k * 2.5 * S, end[1] + uy * 5 * S + ny * k * 2.5 * S),
                 stroke(col(flat or "#c49a6c", alpha), 1.6 * S))
        return
    draw_spear_head(c, hb, tip, ux, uy, nx, ny, S, style, alpha, flat)


def draw_spear_head(c, hb, tip, ux, uy, nx, ny, S, style, alpha=1.0, flat=None):
    hl = math.hypot(tip[0] - hb[0], tip[1] - hb[1])
    w = 5.5 * S
    m = (hb[0] + ux * hl * 0.38, hb[1] + uy * hl * 0.38)
    path = skia.Path()
    path.moveTo(*hb)
    path.lineTo(m[0] + nx * w, m[1] + ny * w)
    path.lineTo(*tip)
    path.lineTo(m[0] - nx * w, m[1] - ny * w)
    path.close()
    c.drawPath(path, fill(col(flat or style.get("steel", "#e9eef2"), alpha)))
    c.drawPath(path, stroke(col(flat or "#1d1612", alpha), 2.0 * S))
    line(c, hb, (hb[0] + ux * hl * 0.85, hb[1] + uy * hl * 0.85),
         stroke(col(flat or "#9aa6b0", alpha), 1.2 * S))
    line(c, (hb[0] - nx * 4 * S, hb[1] - ny * 4 * S), (hb[0] + nx * 4 * S, hb[1] + ny * 4 * S),
         stroke(col(flat or "#c9a24a", alpha), 3.4 * S))


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
    plate = style.get("plate") and not flat
    if plate:
        ol = stroke(col("#1d2430", alpha), W + 4.5 * S)
        polyline(c, [J["sho"], J["elb"], J["hab"]], ol)
        polyline(c, [J["hip"], J["knb"], J["ftb"]], ol)
    limb(c, J, ("sho", "elb", "hab"), pb)
    limb(c, J, ("hip", "knb", "ftb"), pb)
    if style.get("twin") and p.get("nosw2", 0) < 0.5 and "tipb" in J:
        from chain import sword_view
        draw_sword(c, sword_view(J, True), flat or style["steel"], flat or "#222222", alpha, 0,
                   style.get("sword2", "katana"))
    if plate:
        plate_joints(c, J, ("elb", "knb", "hab"), back, S, alpha)
    if style.get("scabbard"):
        draw_scabbard(c, J, flat or style["scab"], flat or style["steel"],
                      flat or "#222222", p["sheath"] > 0.5, alpha)
    if plate:
        polyline(c, [J["hip"], J["knf"], J["ftf"]], stroke(col("#1d2430", alpha), W + 4.5 * S))
        polyline(c, [J["hip"], J["knf"], J["ftf"]], pf)
        plate_joints(c, J, ("knf",), body, S, alpha)
        draw_cuirass(c, J, style, S, alpha)
    else:
        tw = W * style.get("torso", 1.0)
        if J.get("drawn"):   # volume: a stretched torso gets thinner, a squashed one thicker
            tw /= math.sqrt(max(0.6, 1 + J.get("sq", 0.0)))
        limb(c, J, ("hip", "neck"), stroke(col(body, alpha), tw))
        limb(c, J, ("hip", "knf", "ftf"), pf)
    hx, hy = J["head"]
    R = R_HEAD * S * style.get("head", 1.0)
    if headless:
        # bloody stump at the neck
        c.drawCircle(J["neck"][0], J["neck"][1], W * 0.55, fill(col(flat or "#7a0a10", alpha)))
        style = dict(style, band=None, hat=None, horns=None, eye=None, helm=None, topknot=None)
    else:
        sq = J.get("sq", 0.0)
        if abs(sq) > 0.004:
            # squash/stretch: the head goes oval along the neck
            ux_, uy_ = J["head"][0] - J["neck"][0], J["head"][1] - J["neck"][1]
            c.save()
            c.translate(hx, hy)
            c.rotate(math.degrees(math.atan2(uy_, ux_)))
            a_, b_ = R * (1 + sq * 0.9), R * (1 - sq * 0.6)
            c.drawOval(skia.Rect(-a_, -b_, a_, b_), fill(col(body, alpha)))
            c.restore()
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
    if style.get("topknot"):
        draw_topknot(c, hx, hy, ux, uy, rx, ry, R, S, style["body"], style.get("band"), alpha, flat)
    if style.get("helm"):
        draw_helm(c, hx, hy, ux, uy, rx, ry, R, S, style, alpha, flat)
    if style.get("shield") and p.get("noshield", 0) < 0.5:
        ctr, up, ac = shield_frame(J)
        draw_shield(c, ctr, up, ac, S, style, alpha, flat)
    if style.get("eye"):
        ex, ey = hx + J["facing"] * 0 + (d(a + 90)[0] * J["facing"]) * R * 0.45 + ux * R * 0.15, \
            hy + d(a + 90)[1] * R * 0.45 + uy * R * 0.15
        c.drawCircle(ex, ey, 2.2 * S, fill(col(flat or style["eye"], alpha)))
    if style.get("hood") and not headless:
        draw_hood(c, hx, hy, ux, uy, rx, ry, R, S, style, J["facing"], alpha, flat)
    if style.get("sword") == "sickle":
        if p.get("nosw", 0) < 0.5:   # out of the hand: chain.py draws it on the chain
            from chain import draw_sickle
            draw_sickle(c, J, style, alpha, flat)
    elif p.get("nosw", 0) > 0.5:
        pass
    elif style.get("sword") == "scythe":
        if p.get("broken", 0) < 0.5:
            draw_scythe(c, J, style, alpha, flat)
    elif style.get("sword") == "spear":
        draw_spear(c, J, style, alpha, flat, p.get("broken", 0))
    elif p["sheath"] < 0.5 and not style.get("unarmed"):
        draw_sword(c, J, flat or style["steel"], flat or "#222222", alpha,
                   p.get("broken", 0), style.get("sword", "katana"))
    if plate:
        polyline(c, [J["sho"], J["elf"], J["haf"]], stroke(col("#1d2430", alpha), W + 4.5 * S))
    limb(c, J, ("sho", "elf", "haf"), pf)
    if plate:
        plate_joints(c, J, ("elf", "haf"), body, S, alpha)
        pauldron(c, J, body, S, alpha)


# ---------------------------------------------------------------- knight gear
def shield_frame(J):
    """Center of the shield on the back forearm, its long axis (narrow end
    down) and its across axis, in world coords."""
    S = J["size"]
    elb, hab = J["elb"], J["hab"]
    fx_, fy_ = hab[0] - elb[0], hab[1] - elb[1]
    L = max(1e-6, math.hypot(fx_, fy_))
    # forearm angle in the fighter's frame: 0 = up, 90 = forward
    a_f = math.degrees(math.atan2(fx_ * J["facing"], fy_))
    a_s = max(-35.0, min(45.0, a_f * 0.45)) + J["p"].get("rot", 0)
    ax, ay = d(a_s)
    ax *= J["facing"]
    fwd = (J["facing"] * 7 * S, 0)
    cx = hab[0] - fx_ / L * 4 * S + fwd[0] - ax * 6 * S
    cy = hab[1] - fy_ / L * 4 * S - ay * 6 * S
    return (cx, cy), (ax, ay), (ay, -ax)


def shield_path(center, up, across, S, half=0):
    """Kite shield; half = -1 / +1 draws only that side (when it is split)."""
    cx, cy = center
    ux, uy = up
    rx, ry = across
    H1, H2, Wd = 24 * S, 36 * S, 17 * S
    top_l = (cx + ux * H1 - rx * Wd, cy + uy * H1 - ry * Wd)
    top_r = (cx + ux * H1 + rx * Wd, cy + uy * H1 + ry * Wd)
    top_m = (cx + ux * (H1 + 3 * S), cy + uy * (H1 + 3 * S))
    mid_l = (cx - rx * Wd * 1.02, cy - ry * Wd * 1.02)
    mid_r = (cx + rx * Wd * 1.02, cy + ry * Wd * 1.02)
    tip = (cx - ux * H2, cy - uy * H2)
    p = skia.Path()
    if half == 0:
        p.moveTo(*top_l)
        p.quadTo(top_m[0], top_m[1], *top_r)
        p.quadTo(mid_r[0] + ux * 4 * S, mid_r[1] + uy * 4 * S, *mid_r)
        p.quadTo(cx + rx * Wd * 0.6 - ux * H2 * 0.55, cy + ry * Wd * 0.6 - uy * H2 * 0.55, *tip)
        p.quadTo(cx - rx * Wd * 0.6 - ux * H2 * 0.55, cy - ry * Wd * 0.6 - uy * H2 * 0.55, *mid_l)
        p.quadTo(mid_l[0] + ux * 4 * S, mid_l[1] + uy * 4 * S, *top_l)
    else:
        sgn = half
        tl = top_l if sgn < 0 else top_r
        ml = mid_l if sgn < 0 else mid_r
        p.moveTo(*top_m)
        p.lineTo(*tl)
        p.quadTo(ml[0] + ux * 4 * S, ml[1] + uy * 4 * S, *ml)
        p.quadTo(cx + sgn * rx * Wd * 0.6 - ux * H2 * 0.55, cy + sgn * ry * Wd * 0.6 - uy * H2 * 0.55, *tip)
        # jagged split line back up the middle
        for k, u in enumerate((0.75, 0.45, 0.15, -0.2, -0.5, -0.8)):
            j = (3.5 * S if k % 2 else -2.5 * S) * sgn
            p.lineTo(cx - ux * H2 * u + rx * j, cy - uy * H2 * u + ry * j)
    p.close()
    return p


def draw_shield(c, center, up, across, S, style, alpha=1.0, flat=None, half=0):
    p = shield_path(center, up, across, S, half)
    c.drawPath(p, fill(col(flat or style.get("shield", "#2257b8"), alpha)))
    rim = flat or style.get("rim", "#e3b341")
    c.drawPath(p, stroke(col(flat or "#141820", alpha), 5.0 * S))
    c.drawPath(p, stroke(col(rim, alpha), 2.6 * S))
    if flat:
        return
    cx, cy = center
    ux, uy = up
    rx, ry = across
    # gold cross emblem
    cs = col(style.get("rim", "#e3b341"), alpha)
    if half <= 0 or True:
        a0 = (cx + ux * 17 * S, cy + uy * 17 * S)
        a1 = (cx - ux * 22 * S, cy - uy * 22 * S)
        b0 = (cx + ux * 4 * S - rx * 11 * S, cy + uy * 4 * S - ry * 11 * S)
        b1 = (cx + ux * 4 * S + rx * 11 * S, cy + uy * 4 * S + ry * 11 * S)
        c.save()
        c.clipPath(p, skia.ClipOp.kIntersect, True)
        line(c, a0, a1, stroke(cs, 4.2 * S, skia.Paint.kButt_Cap))
        line(c, b0, b1, stroke(cs, 4.2 * S, skia.Paint.kButt_Cap))
        c.restore()


def draw_helm(c, hx, hy, ux, uy, rx, ry, R, S, style, alpha=1.0, flat=None):
    """Great helm: flat-topped steel bucket, eye slit, breaths, plume.

    (ux, uy) points up out of the head, (rx, ry) points forward."""
    steel = flat or style.get("helm", "#c5ccd6")
    dark = flat or "#141820"
    Hh, Hw = R * 1.22, R * 1.12

    def P(a, b):
        return (hx + rx * a + ux * b, hy + ry * a + uy * b)

    p = skia.Path()
    p.moveTo(*P(-Hw, -Hh * 0.95))
    p.lineTo(*P(-Hw, Hh * 0.55))
    p.quadTo(*P(-Hw * 0.9, Hh * 1.05), *P(0, Hh * 1.08))
    p.quadTo(*P(Hw * 0.95, Hh * 1.05), *P(Hw * 1.05, Hh * 0.5))
    p.lineTo(*P(Hw * 1.1, -Hh * 0.7))
    p.quadTo(*P(Hw * 0.9, -Hh * 1.05), *P(Hw * 0.3, -Hh * 1.0))
    p.close()
    if style.get("plume"):
        pc = col(flat or style["plume"], alpha)
        base = P(-Hw * 0.2, Hh * 1.05)
        for k, (bx_, by_, w) in enumerate(((-1.6, 1.9, 5.5), (-2.2, 1.4, 4.5), (-2.4, 0.8, 3.6))):
            pp = skia.Path()
            pp.moveTo(*base)
            m = P(Hw * (bx_ * 0.35), Hh * (by_ + 0.25))
            e = P(Hw * bx_, Hh * by_)
            pp.quadTo(m[0], m[1], e[0], e[1])
            c.drawPath(pp, stroke(pc, w * S))
    c.drawPath(p, fill(col(steel, alpha)))
    c.drawPath(p, stroke(col(dark, alpha), 2.4 * S))
    # eye slit and a vertical nose bar
    line(c, P(-Hw * 0.15, Hh * 0.22), P(Hw * 1.05, Hh * 0.22), stroke(col(dark, alpha), 3.4 * S, skia.Paint.kButt_Cap))
    line(c, P(Hw * 0.55, Hh * 0.6), P(Hw * 0.55, -Hh * 0.9), stroke(col(dark, alpha * 0.55), 1.6 * S))
    if not flat:
        for a, b in ((0.8, -0.3), (0.8, -0.55), (0.62, -0.42)):
            q = P(Hw * a, Hh * b)
            c.drawCircle(q[0], q[1], 1.3 * S, fill(col(dark, alpha)))


def draw_topknot(c, hx, hy, ux, uy, rx, ry, R, S, color, band, alpha=1.0, flat=None):
    k = (hx + ux * R * 0.95 - rx * R * 0.45, hy + uy * R * 0.95 - ry * R * 0.45)
    c.drawCircle(k[0], k[1], 5.2 * S, fill(col(flat or color, alpha)))
    e = (k[0] + ux * 4 * S - rx * 6 * S, k[1] + uy * 4 * S - ry * 6 * S)
    line(c, k, e, stroke(col(flat or color, alpha), 4.2 * S))


# ---------------------------------------------------------------- plate armour
def plate_joints(c, J, names, color, S, alpha=1.0):
    """Couters, poleyns and gauntlets: round steel plates over the joints."""
    for n in names:
        x, y = J[n]
        r = (7.5 if n.startswith("kn") else 6.5) * S
        c.drawCircle(x, y, r, fill(col(color, alpha)))
        c.drawCircle(x, y, r, stroke(col("#1d2430", alpha), 2.2 * S))
        c.drawCircle(x - 1.5 * S, y + 1.5 * S, r * 0.35, fill(col("#ffffff", 0.45 * alpha)))


def pauldron(c, J, color, S, alpha=1.0):
    x, y = J["sho"]
    nx, ny = J["neck"]
    hx, hy = J["hip"]
    L = max(1e-6, math.hypot(nx - hx, ny - hy))
    ux, uy = (nx - hx) / L, (ny - hy) / L
    cx, cy = x - ux * 4 * S, y - uy * 4 * S
    r = 11.5 * S
    p = skia.Path()
    a0 = math.degrees(math.atan2(uy, ux))
    p.addArc(skia.Rect(cx - r, cy - r, cx + r, cy + r), a0 - 95, 190)
    p.close()
    c.drawPath(p, fill(col(color, alpha)))
    c.drawPath(p, stroke(col("#1d2430", alpha), 2.4 * S))
    # lame lines
    for k in (0.55, 0.8):
        rr = r * k
        q = skia.Path()
        q.addArc(skia.Rect(cx - rr, cy - rr, cx + rr, cy + rr), a0 - 80, 160)
        c.drawPath(q, stroke(col("#1d2430", alpha * 0.5), 1.4 * S))


def draw_cuirass(c, J, style, S, alpha=1.0):
    """Breastplate with a blue tabard and a skirt of plates (faulds)."""
    hx, hy = J["hip"]
    nx, ny = J["neck"]
    L = max(1e-6, math.hypot(nx - hx, ny - hy))
    ux, uy = (nx - hx) / L, (ny - hy) / L
    rx, ry = uy * J["facing"], -ux * J["facing"]     # points forward
    def P(a, b):  # a along spine from hip, b forward
        return (hx + ux * a + rx * b, hy + uy * a + ry * b)
    w = 11 * S
    steel, dark = style["body"], "#1d2430"
    # faulds: flared plate skirt over the hips
    f = skia.Path()
    f.moveTo(*P(6 * S, -w))
    f.lineTo(*P(6 * S, w + 2 * S))
    f.lineTo(*P(-16 * S, w + 7 * S))
    f.lineTo(*P(-16 * S, -w - 6 * S))
    f.close()
    c.drawPath(f, fill(col(style.get("back", steel), alpha)))
    c.drawPath(f, stroke(col(dark, alpha), 2.2 * S))
    c.drawLine(*P(-5 * S, -w - 3 * S), *P(-5 * S, w + 4 * S), stroke(col(dark, alpha * 0.6), 1.5 * S))
    # breastplate: rounded front (pigeon chest)
    b = skia.Path()
    b.moveTo(*P(4 * S, -w))
    b.lineTo(*P(L - 2 * S, -w + 1 * S))
    b.quadTo(*P(L + 2 * S, 0), *P(L - 3 * S, w + 1 * S))
    b.quadTo(*P(L * 0.55, w + 6 * S), *P(4 * S, w + 1 * S))
    b.close()
    c.drawPath(b, fill(col(steel, alpha)))
    # tabard over it
    tc = style.get("tabard")
    if tc:
        t = skia.Path()
        t.moveTo(*P(L - 6 * S, -w + 2 * S))
        t.lineTo(*P(L - 6 * S, w - 1 * S))
        t.lineTo(*P(-20 * S, w + 5 * S))
        t.lineTo(*P(-20 * S, -w - 3 * S))
        t.close()
        c.save()
        c.clipPath(b, skia.ClipOp.kIntersect, True)
        c.drawPath(t, fill(col(tc, alpha)))
        c.restore()
        # lower tabard hangs over the faulds
        lo = skia.Path()
        lo.moveTo(*P(6 * S, -w + 2 * S))
        lo.lineTo(*P(6 * S, w))
        lo.lineTo(*P(-22 * S, w + 4 * S))
        lo.lineTo(*P(-22 * S, -w - 2 * S))
        lo.close()
        c.drawPath(lo, fill(col(tc, alpha)))
        c.drawPath(lo, stroke(col(dark, alpha), 2.0 * S))
        # gold belt and cross
        c.drawLine(*P(6 * S, -w - 1 * S), *P(6 * S, w + 2 * S), stroke(col("#e3b341", alpha), 3.4 * S))
        c.drawLine(*P(L * 0.75, -3 * S), *P(L * 0.75, 6 * S), stroke(col("#e3b341", alpha), 2.6 * S))
        c.drawLine(*P(L * 0.9, 1.5 * S), *P(L * 0.45, 1.5 * S), stroke(col("#e3b341", alpha), 2.6 * S))
    c.drawPath(b, stroke(col(dark, alpha), 2.4 * S))
    # gorget at the neck
    g = P(L, 0)
    c.drawCircle(g[0], g[1], 6.5 * S, fill(col(steel, alpha)))
    c.drawCircle(g[0], g[1], 6.5 * S, stroke(col(dark, alpha), 2.0 * S))


# ---------------------------------------------------------------- scythe + hood (fight 07)
def scythe_points(J, style):
    """Adds the scythe blade to the joints: it leaves the top of the snath at
    an angle and curves out to a point (blade_end)."""
    p = J["p"]
    S = J["size"]
    fc = J.get("fx", J["facing"])
    a = p["sw"] + p.get("rot", 0) + style.get("blade_ang", 112)
    bx, by = math.sin(math.radians(a)) * fc, math.cos(math.radians(a))
    sx, sy = J["sw_dir"]
    tip = J["tip"]
    L = style.get("blade_len", 66) * S
    J["blade_end"] = (tip[0] + bx * L - sx * 10 * S, tip[1] + by * L - sy * 10 * S)
    J["blade_ctrl"] = (tip[0] + bx * L * 0.55 + sx * 15 * S, tip[1] + by * L * 0.55 + sy * 15 * S)


def draw_scythe(c, J, style, alpha=1.0, flat=None):
    S = J["size"]
    butt, tip = J["hilt0"], J["tip"]
    dark = flat or "#120c16"
    line(c, butt, tip, stroke(col(dark, alpha), 6.6 * S))
    line(c, butt, tip, stroke(col(flat or style.get("wood", "#3a2a40"), alpha), 3.6 * S))
    # wrapped grips
    for u in (0.18, 0.55):
        q = (butt[0] + (tip[0] - butt[0]) * u, butt[1] + (tip[1] - butt[1]) * u)
        c.drawCircle(q[0], q[1], 3.6 * S, fill(col(flat or style.get("wrap", "#8a6bb8"), alpha)))
    be, ct = J["blade_end"], J["blade_ctrl"]
    sx, sy = J["sw_dir"]
    # crescent: outer curve through ctrl, inner curve pulled toward the shaft
    inner = (ct[0] - sx * 13 * S + (tip[0] - ct[0]) * 0.18, ct[1] - sy * 13 * S + (tip[1] - ct[1]) * 0.18)
    root2 = (tip[0] - sx * 9 * S, tip[1] - sy * 9 * S)
    path = skia.Path()
    path.moveTo(*tip)
    path.quadTo(ct[0], ct[1], be[0], be[1])
    path.quadTo(inner[0], inner[1], root2[0], root2[1])
    path.close()
    c.drawPath(path, fill(col(flat or style.get("steel", "#eef3f7"), alpha)))
    c.drawPath(path, stroke(col(dark, alpha), 2.4 * S))
    if not flat:
        edge = skia.Path()
        edge.moveTo(*root2)
        edge.quadTo(inner[0], inner[1], be[0], be[1])
        c.drawPath(edge, stroke(col(style.get("edge", "#b48cff"), alpha), 1.6 * S))
    c.drawCircle(tip[0], tip[1], 4.2 * S, fill(col(flat or "#c9a24a", alpha)))


def draw_hood(c, hx, hy, ux, uy, rx, ry, R, S, style, fc, alpha=1.0, flat=None):
    """Deep hood with a dark face hole and two glowing eyes (front = +rx side)."""
    hood = flat or style["hood"]
    k = 1.32
    def P(a, b):  # a along up, b toward the face
        return (hx + ux * a * R + rx * b * R, hy + uy * a * R + ry * b * R)
    path = skia.Path()
    path.moveTo(*P(-1.15, 0.95))
    path.quadTo(*P(0.4, 1.35), *P(1.2, 0.35))
    path.quadTo(*P(1.55, -0.6), *P(1.05, -1.55))        # peak hanging back
    path.quadTo(*P(0.2, -1.5), *P(-1.25, -1.05))
    path.quadTo(*P(-1.6, 0.0), *P(-1.15, 0.95))
    path.close()
    c.drawPath(path, fill(col(hood, alpha)))
    if flat:
        return
    face = skia.Path()
    face.addOval(skia.Rect(-0.62 * R, -0.78 * R, 0.62 * R, 0.78 * R))
    m = skia.Matrix()
    m.setRotate(math.degrees(math.atan2(uy, ux)) - 90)
    m.postTranslate(*P(-0.05, 0.42))
    face.transform(m)
    c.drawPath(face, fill(col("#08060a", alpha)))
    glow = style.get("eyes", "#c9a6ff")
    for b in (0.28, 0.72):
        e = P(0.08, b)
        c.drawCircle(e[0], e[1], 3.4 * S, fill(col(glow, alpha * 0.35)))
        c.drawCircle(e[0], e[1], 1.7 * S, fill(col("#ffffff", alpha)))
