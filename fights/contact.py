"""Contact solver: weapons really touch on every clash, blows really land.

Keyframes are posed by eye, so on the frame of a `clash` the two blades are
often a few dozen units apart, and a `hit` can fire while the blade is still
far from the body. The sparks were then drawn in the empty space between them.

For every contact event, in time order, this module:
  1. re-times the event (and its hit-stop / kill cues) by up to a few frames
     to the moment the two shapes are actually closest, then
  2. if they still don't touch, searches a small correction for one fighter
     (weapon angle `sw` and/or hip x), eased in over ~0.1 s before the contact
     and back out after it, so the pose meets exactly on the contact frame.

The contact point it reports is where the shapes touch, so sparks, blood and
impact-frame rays sit on the real collision.
"""
import math

import numpy as np

RAMP_IN, RAMP_OUT, JOIN = 0.11, 0.16, 0.30


# ---------------------------------------------------------------- geometry
def _seg_seg(p1, q1, p2, q2):
    """Closest points between two segments: (dist, point on 1, point on 2, s on 1)."""
    p1, q1, p2, q2 = (np.asarray(v, float) for v in (p1, q1, p2, q2))
    d1, d2, r = q1 - p1, q2 - p2, p1 - p2
    a, e, f = d1 @ d1, d2 @ d2, d2 @ r
    if a < 1e-9 and e < 1e-9:
        return float(np.linalg.norm(p1 - p2)), p1, p2, 0.0
    if a < 1e-9:
        s, t = 0.0, np.clip(f / e, 0, 1)
    else:
        c = d1 @ r
        if e < 1e-9:
            t, s = 0.0, np.clip(-c / a, 0, 1)
        else:
            b = d1 @ d2
            den = a * e - b * b
            s = np.clip((b * f - c * e) / den, 0, 1) if den > 1e-9 else 0.0
            t = (b * s + f) / e
            if t < 0:
                t, s = 0.0, np.clip(-c / a, 0, 1)
            elif t > 1:
                t, s = 1.0, np.clip((b - c) / a, 0, 1)
    c1, c2 = p1 + d1 * s, p2 + d2 * t
    return float(np.linalg.norm(c1 - c2)), c1, c2, float(s)


def weapon_segs(J, st):
    """Hard parts of a fighter's weapon as segments (with a 'blade' flag)."""
    if J["p"].get("sheath", 0) > 0.5 and st.get("sword") not in ("scythe", "spear"):
        return []
    if st.get("sword") == "scythe":
        return [(J["hilt0"], J["tip"], False), (J["tip"], J["blade_end"], True)]
    return [(J["guard"], J["tip"], True)]


def _sub(a, b, u0, u1):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return tuple(a + (b - a) * u0), tuple(a + (b - a) * u1)


def clash_segs(J, st):
    """Parts of a weapon that may meet another weapon in a clash: the blade
    from a quarter of its length out (never the guard, hilt or hands), the
    scythe's crescent, and the upper 55% of its shaft (well away from the
    hands)."""
    if J["p"].get("sheath", 0) > 0.5 and st.get("sword") not in ("scythe", "spear"):
        return []
    if st.get("sword") == "scythe":
        return [_sub(J["hilt0"], J["tip"], 0.45, 1.0), (J["tip"], J["blade_end"])]
    return [_sub(J["guard"], J["tip"], 0.25, 0.97)]


MIN_CROSS = 38.0     # degrees: a block reads as an X, not two parallel sticks


def body_segs(J):
    return [(J["hip"], J["neck"]), (J["neck"], J["head"])]


def shapes(f, kind, kw, JA, JB, a_id, b_id):
    """Two lists of segments that must touch for this event."""
    sa, sb = f.tracks[a_id][1], f.tracks[b_id][1]
    if kind in ("clash", "lock"):
        return clash_segs(JA, sa), clash_segs(JB, sb)
    by = kw.get("by")
    att, vic = (JA, JB) if by == a_id else (JB, JA)
    st = sa if by == a_id else sb
    part = kw.get("part")
    if kind == "decap":
        # the neck must be inside the cutting part of the blade, not under the
        # shaft or the very root of the blade
        tgt = [(vic["neck"], vic["head"])]
        out = []
        for s in weapon_segs(att, st):
            if s[2]:
                a0, b0 = np.asarray(s[0], float), np.asarray(s[1], float)
                out.append((tuple(a0 + (b0 - a0) * 0.35), s[1]))
        return out, tgt
    if part in ("ftf", "ftb", "haf", "hab", "hilt0"):
        knee = {"ftf": "knf", "ftb": "knb", "haf": "elf", "hab": "elb", "hilt0": "hilt0"}[part]
        src = [(att[knee], att[part])] if part != "hilt0" else [(att["hilt0"], att["hilt0"])]
    else:
        src = [(s[0], s[1]) for s in weapon_segs(att, st) if s[2]] or \
              [(s[0], s[1]) for s in weapon_segs(att, st)]
    return src, body_segs(vic)


def gap(sa, sb, cross=False):
    """Distance between two shape lists and the contact point. With cross=True
    a shallow crossing angle (< MIN_CROSS) counts as extra distance."""
    best = (1e9, None)
    for a in sa:
        for b in sb:
            d, c1, c2, _ = _seg_seg(a[0], a[1], b[0], b[1])
            if cross:
                ua = np.subtract(a[1], a[0])
                ub = np.subtract(b[1], b[0])
                cosv = abs(ua @ ub) / max(1e-9, np.linalg.norm(ua) * np.linalg.norm(ub))
                ang = math.degrees(math.acos(min(1.0, cosv)))
                d += max(0.0, MIN_CROSS - ang) * 0.6
            if d < best[0]:
                best = (d, tuple((c1 + c2) / 2))
    return best


def contact_point(f, t):
    """Where the two weapons actually touch (or are closest) at story time t."""
    a_id, b_id = f.ids
    JA, JB = f.joints_raw(a_id, t), f.joints_raw(b_id, t)
    return gap(*shapes(f, "clash", {}, JA, JB, a_id, b_id))


# ---------------------------------------------------------------- corrections
class Corrections:
    """Per-fighter correction curve: keys (t, dsw, dx), eased in and out."""

    def __init__(self):
        self.keys = []

    def set(self, t, dsw, dx):
        self.keys = [k for k in self.keys if abs(k[0] - t) > 1e-6] + [(t, dsw, dx)]
        self.keys.sort()

    def anchors(self):
        out = []
        ks = self.keys
        for i, (t, a, b) in enumerate(ks):
            if i == 0 or t - ks[i - 1][0] > JOIN:
                out.append((t - RAMP_IN, 0.0, 0.0))
            out.append((t, a, b))
            if i == len(ks) - 1 or ks[i + 1][0] - t > JOIN:
                out.append((t + RAMP_OUT, 0.0, 0.0))
        return out

    def at(self, t, anchors=None):
        an = anchors if anchors is not None else self.anchors()
        if not an or t <= an[0][0] or t >= an[-1][0]:
            return 0.0, 0.0
        for (t0, a0, b0), (t1, a1, b1) in zip(an[:-1], an[1:]):
            if t0 <= t <= t1:
                u = (t - t0) / max(1e-9, t1 - t0)
                u = u * u * (3 - 2 * u)
                return a0 + (a1 - a0) * u, b0 + (b1 - b0) * u
        return 0.0, 0.0


TOL = {"clash": 1.5, "lock": 2.0, "hit": 3.0, "decap": 2.0}
LINKED = ("hitstop", "kill", "decap", "dmg", "scrape", "slowmo")


def solve_contacts(f, verbose=False):
    """Fills f.corr[who] and re-times contact events in f.ev in place."""
    ids = f.ids
    f.corr = {i: Corrections() for i in ids}
    f._anch = {i: [] for i in ids}
    a_id, b_id = ids
    report = []
    for t, k, kw in list(f.ev):
        if k == "scrape":
            n = max(2, int(kw["dur"] / 0.08))
            for i in range(1, n + 1):
                f.ev.append((t + kw["dur"] * i / n, "lock", dict(lock=True)))
    order = sorted(range(len(f.ev)), key=lambda j: f.ev[j][0])
    for j in order:
        t, k, kw = f.ev[j]
        if k not in TOL or (k == "hit" and not kw.get("by")):
            continue
        if k == "decap" and not kw.get("by"):
            continue

        def g_at(tt):
            return gap(*shapes(f, k, kw, f.joints_raw(a_id, tt), f.joints_raw(b_id, tt), a_id, b_id),
                       cross=k in ("clash", "lock"))
        g0 = g_at(t)[0]
        # 1. re-time to the closest moment (never later than 2 frames)
        best_t, best_g = t, g0
        for dt in ([] if k == "lock" else np.arange(-0.07, (0.05 if k != "clash" else 0.035), 1 / 240)):
            gg = g_at(t + dt)[0]
            if gg < best_g - 0.5:
                best_t, best_g = t + dt, gg
        if best_t != t:
            _retime(f, j, t, best_t)
            t = best_t
        # 2. pose correction
        g1 = best_g
        if g1 > TOL[k]:
            sol = _search(f, k, kw, t, a_id, b_id)
            if sol:
                who, dsw, dx = sol
                f.corr[who].set(t, dsw, dx)
                f._anch[who] = f.corr[who].anchors()
        g2, pt = g_at(t)
        kw["contact"] = pt
        report.append((round(t, 3), k, round(g0, 1), round(g1, 1), round(g2, 1)))
        if verbose:
            print(f"{k:6s} t={t:6.3f} gap {g0:6.1f} -> retimed {g1:6.1f} -> solved {g2:5.1f}")
    f.ev[:] = [e for e in f.ev if e[1] != "lock"]
    return report


def _retime(f, j, t_old, t_new):
    t, k, kw = f.ev[j]
    f.ev[j] = (t_new, k, kw)
    for i, (tt, kk, kkw) in enumerate(f.ev):
        if i != j and kk in LINKED and abs(tt - t_old) < 0.021:
            f.ev[i] = (tt + (t_new - t_old), kk, kkw)
            for q in ("a1",):
                if q in kkw and abs(kkw[q] - t_old) < 0.021:
                    kkw[q] += t_new - t_old


def _search(f, k, kw, t, a_id, b_id):
    """Smallest (dsw, dx) on one fighter that makes the shapes touch at t
    (a wider search only if the normal range can't reach)."""
    return _search_r(f, k, kw, t, a_id, b_id, 60, 60) or _search_r(f, k, kw, t, a_id, b_id, 110, 130)


def _search_r(f, k, kw, t, a_id, b_id, swr, dxr):
    cands = []
    whos = [a_id, b_id]
    if k in ("hit", "decap"):
        att = kw["by"]
        vic = b_id if att == a_id else a_id
        whos = [att, vic]
    for who in whos:
        armed = True
        if k not in ("clash", "lock"):
            armed = who == kw["by"] and kw.get("part") not in ("ftf", "ftb", "haf", "hab")
        sw_range = np.arange(-swr, swr + 1, 5) if armed else [0.0]
        dx_range = np.arange(-dxr, dxr + 1, 6)
        old = list(f.corr[who].keys)
        best = None
        for dsw in sw_range:
            for dx in dx_range:
                cost = abs(dsw) / 22 + abs(dx) / 14
                if best and cost >= best[0]:
                    continue
                g = _try(f, k, kw, t, a_id, b_id, who, old, dsw, dx)
                if g <= TOL[k]:
                    best = (cost, dsw, dx)
        if best:
            # refine around the best
            c0, s0, x0 = best
            for dsw in np.arange(s0 - 4, s0 + 4.1, 1) if armed else [0.0]:
                for dx in np.arange(x0 - 5, x0 + 5.1, 1):
                    cost = abs(dsw) / 22 + abs(dx) / 14
                    if cost < best[0] and _try(f, k, kw, t, a_id, b_id, who, old, dsw, dx) <= TOL[k]:
                        best = (cost, dsw, dx)
            cands.append((best[0] + (0.0 if who == whos[0] else 0.4), who, best[1], best[2]))
        f.corr[who].keys = old
        f._anch[who] = f.corr[who].anchors()
    if not cands:
        return None
    _, who, dsw, dx = min(cands)
    return who, float(dsw), float(dx)


def _try(f, k, kw, t, a_id, b_id, who, old, dsw, dx):
    f.corr[who].keys = old
    f.corr[who].set(t, dsw, dx)
    f._anch[who] = f.corr[who].anchors()
    JA, JB = f.joints_raw(a_id, t), f.joints_raw(b_id, t)
    return gap(*shapes(f, k, kw, JA, JB, a_id, b_id), cross=k in ("clash", "lock"))[0]
