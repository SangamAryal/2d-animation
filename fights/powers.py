"""Time stop and future sight for the fight renderer.

Events
  tstop   who, dur, windup   time freezes for everyone but `who` for `dur`
                             seconds of anim time starting at t
  tbreak  who                the stop gesture is cut short (dial shatters)
  vision  who, on, dur, lead `who` sees `on` `lead` seconds ahead for `dur`

While time is stopped the world is drawn desaturated, effects (blood, sparks)
hang in the air, and damage dealt is only applied when time resumes.
"""
import math

import numpy as np
import skia

from draw import col, draw_fighter, fill, stroke
from rig import R_HEAD

KINDS = {"tstop", "tbreak", "vision"}
GOLD, VIOLET, SIGHT = "#f2c14e", "#8f6cff", "#5ff4ff"


def clamp(u):
    return max(0.0, min(1.0, u))


def init(r):
    r.tstops = []     # (t0, t1, who, windup)
    r.tstops_vt = []  # (vt0, vt1)
    r.visions = []    # (t0, t1, who, on, lead)
    r.tbreaks = []    # (t, who)


def prepare(r, t, vt, k, kw):
    if k not in KINDS:
        return False
    from render import video_time
    if k == "tstop":
        t1 = t + kw["dur"]
        w = kw.get("windup", 0.35)
        r.tstops.append((t, t1, kw["who"], w))
        r.tstops_vt.append((vt, video_time(r.frames, t1)))
        r.cues.append((video_time(r.frames, t - w), "tstop_wind", dict(dur=vt - video_time(r.frames, t - w))))
        r.cues.append((vt, "tstop", {}))
        tt, i = t + 0.5, 0
        while tt < t1 - 0.05:      # one tick-tock per half second of stopped time
            r.cues.append((video_time(r.frames, tt), "tick", dict(v=1.0, i=i)))
            tt += 0.25
            i += 1
        r.cues.append((video_time(r.frames, t1), "tresume", {}))
    elif k == "tbreak":
        r.tbreaks.append((t, kw["who"]))
        r.cues.append((vt, "tbreak", {}))
    elif k == "vision":
        r.visions.append((t, t + kw["dur"], kw["who"], kw["on"], kw.get("lead", 0.4)))
        r.cues.append((vt, "vision", dict(dur=kw["dur"])))
    return True


def finish(r):
    """Damage dealt in stopped time lands when time resumes."""
    out = []
    for vt, who, amt in r.damage:
        for a, b in r.tstops_vt:
            if a <= vt < b:
                vt = b
        out.append((vt, who, amt))
    r.damage = out


def wclock(r, vt):
    """Video time with stopped time taken out: the world's own clock."""
    w = vt
    for a, b in r.tstops_vt:
        w -= max(0.0, min(vt, b) - a)
    return w


def wdt(r, vt, et):
    """Elapsed world time since an effect started (frozen during a stop)."""
    if vt < et:
        return -1.0
    d = wclock(r, vt) - wclock(r, et)
    if d < 0.05 and stopped_vt(r, vt):
        d = min(vt - et, 0.05)    # let it burst a little, then hang
    return d


def stopped_vt(r, vt):
    return any(a <= vt < b for a, b in r.tstops_vt)


def stop_state(r, t):
    """(who, gray amount 0..1, t0, t1) for the stop active at anim time t."""
    for t0, t1, who, w in r.tstops:
        if t0 <= t < t1 + 0.12:
            g = clamp((t - t0) / 0.12) if t < t1 else clamp(1 - (t - t1) / 0.12)
            return who, g, t0, t1
    return None, 0.0, 0, 0


def gray_paint(g):
    """Desaturate with a cold violet cast, mixed with the original by g."""
    lr, lg, lb = 0.30, 0.59, 0.11
    tint = (0.92, 0.90, 1.08)
    m = []
    for i in range(3):
        row = [0.0] * 5
        for j, l in enumerate((lr, lg, lb)):
            ident = 1.0 if i == j else 0.0
            row[j] = ident * (1 - g) + l * tint[i] * 0.95 * g
        row[4] = 0.0
        m += row
    m += [0, 0, 0, 1, 0]
    p = skia.Paint()
    p.setColorFilter(skia.ColorFilters.Matrix(m))
    return p


def eye_point(J, style):
    hx, hy = J["head"]
    a = math.radians(J["p"]["H"] + J["p"].get("rot", 0))
    R = R_HEAD * J["size"] * style.get("head", 1.0)
    ux, uy = math.sin(a) * J["facing"], math.cos(a)
    rx, ry = math.sin(a + math.pi / 2) * J["facing"], math.cos(a + math.pi / 2)
    return hx + rx * R * 0.45 + ux * R * 0.15, hy + ry * R * 0.45 + uy * R * 0.15


def dial(c, x, y, rad, a, hand, color=GOLD, w=4.0):
    """A clock face: ring, twelve ticks and one sweeping hand."""
    c.drawCircle(x, y, rad, stroke(col(color, a), w))
    for i in range(12):
        an = i / 12 * 2 * math.pi
        r0 = rad * (0.78 if i % 3 == 0 else 0.86)
        c.drawLine(x + math.cos(an) * r0, y + math.sin(an) * r0,
                   x + math.cos(an) * rad, y + math.sin(an) * rad, stroke(col(color, a), w * 0.8))
    c.drawLine(x, y, x + math.sin(hand) * rad * 0.7, y + math.cos(hand) * rad * 0.7,
               stroke(col(color, a), w * 1.1))


# ------------------------------------------------------------ world layer
def draw_world(r, c, t, vt, flat):
    """Inside the world transform, behind the fighters: future-sight ghosts."""
    if flat:
        return
    f = r.f
    for t0, t1, who, on, lead in r.visions:
        if not (t0 <= t < t1 + 0.2):
            continue
        fade = clamp((t - t0) / 0.12) * clamp((t1 + 0.2 - t) / 0.2)
        style = f.tracks[on][1]
        for k, a in ((1.0, 0.42), (0.66, 0.22), (0.33, 0.12)):
            J = f.joints(on, t + lead * k)
            draw_fighter(c, J, style, alpha=a * fade, flat=SIGHT)


def draw_front(r, c, t, vt, flat):
    """Inside the world transform, after the fighters."""
    f = r.f
    # stop gesture: a dial gathering at the raised hand
    for t0, t1, who, w in r.tstops:
        if t0 - w <= t < t0 + 0.1:
            J = f.joints(who, t)
            x, y = J["hab"]
            u = clamp((t - (t0 - w)) / w)
            dial(c, x, y + 4, 10 + 22 * u, 0.9, -t * 9, flat or GOLD, 3)
            c.drawCircle(x, y + 4, 6 + 10 * u, fill(col(flat or "#fff3c4", 0.6 * u)))
    for tb, who in r.tbreaks:
        d = t - tb
        if 0 <= d < 0.7:
            J = f.joints(who, tb)
            x, y = J["hab"]
            rng = np.random.default_rng(int(tb * 100))
            for i in range(14):
                an = rng.uniform(0, 2 * math.pi)
                sp = rng.uniform(180, 520)
                px = x + math.cos(an) * sp * d
                py = y + math.sin(an) * sp * d - 500 * d * d
                L = rng.uniform(6, 14)
                c.drawLine(px, py, px + math.cos(an + d * 8) * L, py + math.sin(an + d * 8) * L,
                           stroke(col(flat or GOLD, 1 - d / 0.7), 3))
    # seer's eyes glow while he looks ahead
    for t0, t1, who, on, lead in r.visions:
        if t0 - 0.05 <= t < t1 + 0.25:
            u = clamp((t - t0 + 0.05) / 0.1) * clamp((t1 + 0.25 - t) / 0.25)
            J = f.joints(who, t)
            ex, ey = eye_point(J, f.tracks[who][1])
            c.drawCircle(ex, ey, 9 * u, fill(col(flat or SIGHT, 0.35 * u)))
            c.drawCircle(ex, ey, 3.2, fill(col(flat or "#ffffff", u)))
            L = 26 * u
            c.drawLine(ex, ey, ex + J["facing"] * L, ey + 2, stroke(col(flat or SIGHT, 0.8 * u), 2))


# ------------------------------------------------------------ screen layer
def draw_screen(r, c, t, vt):
    """After the world: activation rings, vision tint and the countdown."""
    from render import typeface
    W, H, s = r.W, r.H, r.s
    who, g, t0, t1 = stop_state(r, t)
    for a0, a1, w_, wu in r.tstops:
        J = r.f.joints(w_, a0)
        cx, z = r.cams[min(len(r.cams) - 1, int(vt * 60))]
        sx = W / 2 + (J["sho"][0] - cx) * z
        sy = r.gy - J["sho"][1] * z
        d = t - a0
        if 0 <= d < 0.45:   # time freezes: a dial sweeps out over the screen
            u = d / 0.45
            rad = (60 + u * 2.2 * H) * (1 if r.wide else 1)
            dial(c, sx, sy, rad, 1 - u, u * 6, GOLD, 10 * s * (1 - u) + 2)
            c.drawCircle(sx, sy, rad * 0.97, stroke(col("#ffffff", 0.5 * (1 - u)), 30 * s))
        d = t - a1
        if 0 <= d < 0.3:    # time flows again: the dial snaps back
            u = d / 0.3
            rad = (1 - u) * 1.4 * H + 20
            dial(c, sx, sy, rad, 1 - u, -u * 6, "#ffffff", 8 * s * (1 - u) + 2)
    if g > 0:
        # vignette + countdown
        rem = max(0.0, t1 - t)
        top = (0.16 if not r.wide else 0.13) * H + 140 * s
        cx_ = W / 2
        rad = 52 * s
        c.drawCircle(cx_, top + rad, rad + 10 * s, fill(col("#1b1714", 0.75 * g)))
        sweep = 360 * rem / (t1 - t0)
        p = skia.Path()
        p.addArc(skia.Rect(cx_ - rad, top, cx_ + rad, top + 2 * rad), -90, sweep)
        c.drawPath(p, stroke(col(GOLD, g), 9 * s))
        font = skia.Font(typeface("ExtraBold"), 44 * s)
        txt = f"{rem:.1f}"
        tw = font.measureText(txt)
        c.drawString(txt, cx_ - tw / 2, top + rad + 15 * s, font, fill(col("#ffffff", g)))
        small = skia.Font(typeface("Bold"), 26 * s)
        lab = "TIME STOPPED"
        lw = small.measureText(lab)
        c.drawString(lab, cx_ - lw / 2, top + 2 * rad + 50 * s, small, fill(col(GOLD, g)))
    for v0, v1, w_, on, lead in r.visions:
        if v0 <= t < v1 + 0.2:
            u = clamp((t - v0) / 0.1) * clamp((v1 + 0.2 - t) / 0.2)
            p = skia.Paint()
            p.setShader(skia.GradientShader.MakeRadial(
                (W / 2, H / 2), max(W, H) * 0.75,
                [col(SIGHT, 0.0).toColor(), col(SIGHT, 0.22 * u).toColor()], [0.55, 1.0]))
            c.drawRect(skia.Rect(0, 0, W, H), p)
