"""Breakable scenery for the cliff-edge fight (theme "cliff").

The meadow ends at a cliff edge; past it the ground drops into a misty valley.
A fight dict may carry  terrain=dict(edge=X, tree=X, boulder=X)  and these
events change the scene:

  E(t, "treecut", dir=+1|-1, h=40)       the pine is cut h units up and falls
                                          toward dir (lands ~0.9 s later)
  E(t, "rocksmash", dir=+1|-1, v=1.0)    the boulder bursts into flying chunks
  E(t, "ledge", x0=X)                    the ground past x0 breaks off and
                                          falls into the valley (new edge = x0)
  E(t, "pebbles", x=X, n=6)              a few stones skitter off the edge

All shapes are in world units (y up, ground at 0) and drawn inside the camera
transform, behind the fighters.
"""
import math

import numpy as np
import skia

from draw import col, fill, line, polyline, stroke

G = 1500.0
TREE_H = 300.0


def init(r):
    f = r.f
    tr = getattr(f, "terrain", None) or {}
    r.ter = dict(tr)
    r.ter_ev = [(t, k, kw) for t, k, kw in f.ev if k in ("treecut", "rocksmash", "ledge", "pebbles")]
    r.ter_frags = []
    for t, k, kw in r.ter_ev:
        if k == "rocksmash":
            rng = np.random.default_rng(int(t * 1000) % 9973)
            d = kw.get("dir", 1)
            for i in range(9):
                big = i < 4
                r.ter_frags.append(dict(
                    t0=t, x=tr["boulder"] + rng.uniform(-30, 30), y=rng.uniform(20, 70),
                    vx=d * rng.uniform(250, 900) * kw.get("v", 1.0) * (0.7 if big else 1.0),
                    vy=rng.uniform(150, 650), w=rng.uniform(-14, 14),
                    r=rng.uniform(13, 22) if big else rng.uniform(6, 11), seed=int(rng.integers(1e6))))
        if k in ("pebbles", "ledge"):
            rng = np.random.default_rng(int(t * 997) % 9973)
            x0 = kw.get("x", kw.get("x0", tr.get("edge", 0)))
            n = kw.get("n", 6 if k == "pebbles" else 16)
            for i in range(n):
                r.ter_frags.append(dict(
                    t0=t + rng.uniform(0, 0.25), x=x0 + rng.uniform(-10, 60 if k == "ledge" else 14),
                    y=rng.uniform(2, 20), vx=rng.uniform(20, 160), vy=rng.uniform(20, 200),
                    w=rng.uniform(-10, 10), r=rng.uniform(3, 7) if k == "pebbles" else rng.uniform(5, 14),
                    seed=int(rng.integers(1e6)), fall=True))


def edge_at(r, t):
    e = r.ter.get("edge")
    if e is None:
        return None
    for tt, k, kw in r.ter_ev:
        if k == "ledge" and t >= tt:
            e = min(e, kw["x0"])
    return e


# ------------------------------------------------------------------ chasm
def draw_chasm(r, c, t, flat):
    """Everything past the edge: the drop, misty valley far below, the rock
    face under the lip. Drawn in world space right after the background."""
    e = edge_at(r, t)
    if e is None or flat:
        return
    # the valley: mist gradient over the cut-away floor
    p = skia.Paint()
    p.setShader(skia.GradientShader.MakeLinear(
        [(0, 10), (0, -700)], [col("#c9dbe6").toColor(), col("#7f98ad").toColor()]))
    c.drawRect(skia.Rect(e, 10, e + 6000, -6000), p)
    # the valley far below: forested ridges, a little mist between them
    for depth, colr, amp, seed in ((-60, "#9db7c2", 40, 0.4), (-170, "#7e9f99", 55, 1.0),
                                   (-300, "#5f8572", 70, 2.3), (-460, "#4b6f5a", 80, 3.1)):
        path = skia.Path()
        path.moveTo(e, -6000)
        for i in range(0, 80):
            x = e + i * 50
            y = depth + amp * (0.6 * math.sin(x * 0.006 + seed) + 0.4 * math.sin(x * 0.017 + seed * 2))
            path.lineTo(x, y)
        path.lineTo(e + 4000, -6000)
        path.close()
        c.drawPath(path, fill(col(colr)))
        # tiny far pines along the ridge line
        for i in range(0, 80, 2):
            x = e + i * 50 + 17
            y = depth + amp * (0.6 * math.sin(x * 0.006 + seed) + 0.4 * math.sin(x * 0.017 + seed * 2))
            tp = skia.Path()
            tp.moveTo(x - 7, y - 2)
            tp.lineTo(x, y + 18)
            tp.lineTo(x + 7, y - 2)
            tp.close()
            c.drawPath(tp, fill(col(colr)))
    # the rock face under the lip
    rng = np.random.default_rng(5)
    face = skia.Path()
    face.moveTo(e - 60, 0)
    face.lineTo(e, 0)
    y = 0.0
    xs = []
    while y > -2400:
        y -= rng.uniform(40, 90)
        x = e + rng.uniform(-22, 14) - (-y) * 0.04
        xs.append((x, y))
        face.lineTo(x, y)
    face.lineTo(e - 260, y)
    face.close()
    c.drawPath(face, fill(col("#7d6d5c")))
    polyline(c, [(e, 0)] + xs, stroke(col("#4a3d31"), 3))
    for i, (x, y) in enumerate(xs[:-1]):
        if i % 2 == 0:
            c.drawLine(x - 4, y, x - 30, y - 18, stroke(col("#5e5144", 0.8), 2))
    # grass lip hanging over
    c.drawRect(skia.Rect(e - 40, 2, e + 2, -9), fill(col("#5f9a45")))
    for k in range(4):
        x = e - 6 - k * 9
        c.drawLine(x, -9, x + 2, -16 - (k % 2) * 6, stroke(col("#4d8a37"), 2.4))


# ------------------------------------------------------------------ props
def _tree_shape(c, base, ang, h0, h1, flat):
    """Pine trunk segment from height h0 to h1 (unrotated), drawn rotated by
    ang (deg, + falls toward +x) around base."""
    c.save()
    c.translate(*base)
    c.rotate(-ang)
    trunk = flat or "#6b4a30"
    c.drawRect(skia.Rect(-8, h0, 8, h1), fill(col(trunk)))
    c.drawLine(-8, h0, -8, h1, stroke(col(flat or "#3b281a"), 2.5))
    c.drawLine(8, h0, 8, h1, stroke(col(flat or "#3b281a"), 2.5))
    if h1 > 120:
        for j, (yb, w, hh) in enumerate(((95, 82, 110), (150, 66, 100), (200, 50, 90), (245, 34, 70))):
            if yb < h0:
                continue
            path = skia.Path()
            path.moveTo(-w, yb)
            path.lineTo(0, yb + hh)
            path.lineTo(w, yb)
            path.close()
            c.drawPath(path, fill(col(flat or ("#2f6b3a" if j % 2 == 0 else "#357643"))))
            c.drawPath(path, stroke(col(flat or "#1f4a28"), 2.5))
    c.restore()


def tree_fall(r, t):
    """(cut, angle, cut height) for the pine at story time t."""
    for tt, k, kw in r.ter_ev:
        if k == "treecut" and t >= tt:
            s = t - tt
            d = kw.get("dir", 1)
            # slow tip-over, accelerating, one small bounce on landing
            T = kw.get("dur", 0.9)
            if s < T:
                a = 90 * (s / T) ** 2.2
            else:
                b = s - T
                a = 90 - 7 * math.exp(-b * 6) * abs(math.sin(b * 12))
            return True, d * a, kw.get("h", 40)
    return False, 0.0, 0.0


def draw_props(r, c, t, flat):
    tr = r.ter
    if "tree" in tr:
        x = tr["tree"]
        cut, a, h = tree_fall(r, t)
        if not cut:
            _tree_shape(c, (x, 0), 0, 0, TREE_H, flat)
        else:
            _tree_shape(c, (x, 0), 0, 0, h, flat)        # stump
            c.drawLine(x - 9, h, x + 9, h, stroke(col(flat or "#e0c79a"), 3))
            _tree_shape(c, (x, h), a, 0, TREE_H - h, flat)
    if "boulder" in tr:
        smashed = any(k == "rocksmash" and t >= tt for tt, k, kw in r.ter_ev)
        if not smashed:
            bx = tr["boulder"]
            rng = np.random.default_rng(3)
            path = skia.Path()
            n = 11
            for i in range(n + 1):
                a = math.pi * i / n
                rr = 60 * (1 + 0.12 * math.sin(i * 2.7))
                pt = (bx + math.cos(a) * rr * 1.15, max(0.0, math.sin(a) * rr * 0.95))
                if i == 0:
                    path.moveTo(*pt)
                else:
                    path.lineTo(*pt)
            path.close()
            c.drawPath(path, fill(col(flat or "#8d8a84")))
            c.drawPath(path, stroke(col(flat or "#4b4844"), 3))
            if not flat:
                for k in range(3):
                    c.drawLine(bx - 30 + k * 22, 18 + k * 9, bx - 14 + k * 20, 34 + k * 7,
                               stroke(col("#6c6964"), 2.2))
            del rng
    draw_frags(r, c, t, flat)
    draw_ledge(r, c, t, flat)


def frag_state(r, fr, t):
    s = t - fr["t0"]
    e = edge_at(r, t)
    x = fr["x"] + fr["vx"] * s
    y = fr["y"] + fr["vy"] * s - 0.5 * G * s * s
    rot = fr["w"] * s * 57
    over = e is not None and x > e
    if y < fr["r"] * 0.6 and not over:
        # landed: find landing time, then a short roll
        a, b, cc = -0.5 * G, fr["vy"], fr["y"] - fr["r"] * 0.6
        sl = (-b - math.sqrt(max(0.0, b * b - 4 * a * cc))) / (2 * a)
        xl = fr["x"] + fr["vx"] * sl
        roll = fr["vx"] * 0.25 * (1 - math.exp(-(s - sl) * 4))
        x = xl + roll
        y = fr["r"] * 0.6
        rot = fr["w"] * sl * 57 + roll * 2
        if e is not None and x > e:      # rolled over the edge: drop
            y = fr["r"] * 0.6 - 0.5 * G * max(0.0, s - sl - 0.25) ** 2
    return x, y, rot


def draw_frags(r, c, t, flat):
    for fr in r.ter_frags:
        if t < fr["t0"] or t - fr["t0"] > 6:
            continue
        x, y, rot = frag_state(r, fr, t)
        if y < -1500:
            continue
        rng = np.random.default_rng(fr["seed"])
        path = skia.Path()
        n = 6
        for i in range(n):
            a = math.radians(rot) + 2 * math.pi * i / n
            rr = fr["r"] * rng.uniform(0.7, 1.2)
            pt = (x + math.cos(a) * rr, y + math.sin(a) * rr)
            if i == 0:
                path.moveTo(*pt)
            else:
                path.lineTo(*pt)
        path.close()
        c.drawPath(path, fill(col(flat or "#8d8a84")))
        c.drawPath(path, stroke(col(flat or "#4b4844"), 2))


def draw_ledge(r, c, t, flat):
    """The chunk of ground that broke off: grass on top, rock under it,
    tipping outward and dropping into the valley."""
    for tt, k, kw in r.ter_ev:
        if k != "ledge" or t < tt:
            continue
        s = t - tt
        if s > 3:
            continue
        x0, x1 = kw["x0"], r.ter["edge"]
        dy = -0.5 * G * 0.8 * s * s
        ang = 26 * s * s + 8 * s
        c.save()
        c.translate(x0, dy)
        c.rotate(-ang)
        w = x1 - x0
        path = skia.Path()
        path.moveTo(0, 0)
        path.lineTo(w, 0)
        path.lineTo(w - 20, -60)
        path.lineTo(w * 0.6, -120)
        path.lineTo(w * 0.25, -95)
        path.lineTo(8, -40)
        path.close()
        c.drawPath(path, fill(col(flat or "#7d6d5c")))
        c.drawPath(path, stroke(col(flat or "#4a3d31"), 3))
        c.drawRect(skia.Rect(0, 4, w, -8), fill(col(flat or "#5f9a45")))
        c.restore()


def ground_mask(r, c, t, flat):
    """Called right after the background: cut the floor away past the edge."""
    draw_chasm(r, c, t, flat)
