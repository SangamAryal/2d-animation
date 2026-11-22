"""Fight 08 gear: twin swords, the kusarigama (sickle + weighted chain) and
loose swords (thrown, deflected, caught, disarmed, stuck in the ground).

The chain is a real rope: a verlet simulation run once over the whole story
timeline (1/240 s steps), so it has inertia, sags, whips, goes taut and
recoils by itself. Two ropes make up the kusarigama:

* the held loop, from the butt of the sickle handle (hilt0) to the back hand
  (hab), fixed length; pull the hands apart and it goes taut (used to catch
  blades), bring them together and it sags;
* the free chain, from the back hand to the weight. Its length follows the
  pose key ``reel`` (how much chain is let out); while the weight is driven
  the chain pays out as far as it needs to.

The weight is free (pure physics) unless a ``chain`` event drives it:

  E(t, "chain", mode="spin", dur=, r=, turns=, plane="over"|"side", c=(dx, dy))
  E(t, "chain", mode="path", dur=, pts=[wp, ...], ease="out", hold=False)
  E(t, "chain", mode="attach", dur=, to=("B", "hilt0", "guard", 0.5))
  E(t, "chain", mode="loose", dur=, sword=k)     # rides a loose sword
  E(t, "chain", mode="free")

A waypoint is (x, y) in world units, or ("J", who, key, dx, dy) (follows a
joint; dx is along that fighter's facing), evaluated at every step, so a
throw lands where the target *is*, not where it was.

Loose swords come from ``loose`` events, see LooseSword.
"""
import math

import numpy as np
import skia

from draw import col, fill, line, polyline, stroke

DT = 1 / 240
G = 1250.0


# ---------------------------------------------------------------- joints
def twin_points(J, st):
    """Second sword in the back hand, angle p["sw2"]."""
    p = J["p"]
    S = J["size"]
    fx = J.get("fx", J["facing"])
    a = math.radians(p["sw2"] + p.get("rot", 0.0))
    ux, uy = math.sin(a) * fx, math.cos(a)
    hx, hy = J["hab"]
    bl = st.get("blade", 72)
    butt = st.get("butt", 8.0)
    J["hilt0b"] = (hx - ux * butt * S, hy - uy * butt * S)
    J["guardb"] = (hx + ux * 12 * S, hy + uy * 12 * S)
    J["tipb"] = (hx + ux * (12 + bl) * S, hy + uy * (12 + bl) * S)
    J["sw2_dir"] = (ux, uy)


def sickle_points(J, st):
    """Kama blade: leaves the top of the handle at blade_ang and curves to a point."""
    p = J["p"]
    S = J["size"]
    fc = J.get("fx", J["facing"])
    a = p["sw"] + p.get("rot", 0) + st.get("blade_ang", 96)
    bx, by = math.sin(math.radians(a)) * fc, math.cos(math.radians(a))
    sx, sy = J["sw_dir"]
    tip = J["tip"]
    L = st.get("blade_len", 40) * S
    J["blade_end"] = (tip[0] + bx * L - sx * 7 * S, tip[1] + by * L - sy * 7 * S)
    J["blade_ctrl"] = (tip[0] + bx * L * 0.55 + sx * 8 * S, tip[1] + by * L * 0.55 + sy * 8 * S)


def sword_view(J, second):
    """A J-like dict whose hilt0/guard/tip/sw_dir are one of the twin swords."""
    if not second:
        return J
    K = dict(J)
    K["hilt0"], K["guard"], K["tip"], K["sw_dir"] = J["hilt0b"], J["guardb"], J["tipb"], J["sw2_dir"]
    return K


def draw_sickle(c, J, style, alpha=1.0, flat=None):
    S = J["size"]
    butt, tip = J["hilt0"], J["tip"]
    dark = flat or "#15171c"
    line(c, butt, tip, stroke(col(dark, alpha), 6.2 * S))
    line(c, butt, tip, stroke(col(flat or style.get("wood", "#6b4a2e"), alpha), 3.4 * S))
    for u in (0.12, 0.3, 0.48):
        q = (butt[0] + (tip[0] - butt[0]) * u, butt[1] + (tip[1] - butt[1]) * u)
        c.drawCircle(q[0], q[1], 2.6 * S, fill(col(flat or style.get("wrap", "#2a2f3a"), alpha)))
    be, ct = J["blade_end"], J["blade_ctrl"]
    sx, sy = J["sw_dir"]
    inner = (ct[0] - sx * 7 * S + (tip[0] - ct[0]) * 0.2, ct[1] - sy * 7 * S + (tip[1] - ct[1]) * 0.2)
    root2 = (tip[0] - sx * 6 * S, tip[1] - sy * 6 * S)
    path = skia.Path()
    path.moveTo(*tip)
    path.quadTo(ct[0], ct[1], be[0], be[1])
    path.quadTo(inner[0], inner[1], root2[0], root2[1])
    path.close()
    c.drawPath(path, fill(col(flat or style.get("steel", "#eef3f7"), alpha)))
    c.drawPath(path, stroke(col(dark, alpha), 2.2 * S))
    if not flat:
        edge = skia.Path()
        edge.moveTo(*root2)
        edge.quadTo(inner[0], inner[1], be[0], be[1])
        c.drawPath(edge, stroke(col(style.get("edge", "#ffb347"), alpha), 1.4 * S))
    c.drawCircle(tip[0], tip[1], 3.4 * S, fill(col(flat or "#c9a24a", alpha)))
    c.drawCircle(butt[0], butt[1], 3.0 * S, fill(col(flat or "#8d939c", alpha)))


# ---------------------------------------------------------------- helpers
def _cr(p0, p1, p2, p3, u):
    u2, u3 = u * u, u * u * u
    return tuple(0.5 * ((2 * p1[k]) + (-p0[k] + p2[k]) * u + (2 * p0[k] - 5 * p1[k] + 4 * p2[k] - p3[k]) * u2
                        + (-p0[k] + 3 * p1[k] - 3 * p2[k] + p3[k]) * u3) for k in (0, 1))


def _ease(kind, u):
    from rig import ease
    return ease(kind, u)


def _smooth(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


# ---------------------------------------------------------------- loose swords
class LooseSword:
    """A sword out of the hand.

    kind "throw": thrown at t0 from (who, second) toward point D at td (the
    deflection), then a ballistic arc back into the thrower's hand at tc.
    kind "fling": leaves the hand at t0 (yanked by the chain) and flies on a
    ballistic arc that sticks it in the ground at (xl, 0) at tl.
    Center = middle of the blade; ang = world angle of the blade (0 up, cw).
    """

    def __init__(self, f, kw):
        self.kw = kw
        self.who = kw["who"]
        self.second = kw.get("second", False)
        st = f.tracks[self.who][1]
        self.bl = st.get("blade", 72)
        self.S = st.get("size", 1.0)
        self.steel = st.get("steel", "#e9eef2")
        self.kind = kw["lk"]
        self.t0 = kw["t0"]
        J = f.joints_raw(self.who, self.t0)
        K = sword_view(J, self.second)
        self.c0 = self._center(K)
        self.a0 = self._ang(K)
        self.t_end = 1e9
        if self.kind == "throw":
            self.td, self.tc = kw["td"], kw["tc"]
            JD = f.joints_raw(kw["at"], self.td)
            self.D = kw.get("D") or ((JD["tip"][0] + JD["blade_end"][0]) / 2,
                                     (JD["tip"][1] + JD["blade_end"][1]) / 2)
            sa = kw.get("cross_ang")
            if sa is None:   # blade crossing the sickle blade at ~90 deg
                bx, by = JD["blade_end"][0] - JD["tip"][0], JD["blade_end"][1] - JD["tip"][1]
                sa = math.degrees(math.atan2(bx, by)) + 90
            self.ad = self.a0 + self._turns(sa - self.a0, kw.get("spin1", 2))
            JC = f.joints_raw(self.who, self.tc)
            KC = sword_view(JC, self.second)
            self.C = self._center(KC)
            self.ac = self.ad + self._turns(self._ang(KC) - self.ad, kw.get("spin2", -2))
            T = self.tc - self.td
            self.v0 = ((self.C[0] - self.D[0]) / T, (self.C[1] - self.D[1] + 0.5 * G * T * T) / T)
            self.t_end = self.tc
        else:
            self.tl = kw["tl"]
            self.L = (kw["xl"], kw.get("yl", 18.0 * self.S))
            T = self.tl - self.t0
            self.v0 = ((self.L[0] - self.c0[0]) / T, (self.L[1] - self.c0[1] + 0.5 * G * T * T) / T)
            self.al = self.a0 + self._turns(kw.get("land_ang", 172) - self.a0, kw.get("spin", 2))

    @staticmethod
    def _turns(d, n):
        d = (d + 180) % 360 - 180
        return d + 360 * n

    def _center(self, K):
        g, tp = K["guard"], K["tip"]
        return ((g[0] + tp[0]) / 2, (g[1] + tp[1]) / 2)

    @staticmethod
    def _ang(K):
        ux, uy = K["tip"][0] - K["guard"][0], K["tip"][1] - K["guard"][1]
        return math.degrees(math.atan2(ux, uy))

    def active(self, t):
        return self.t0 <= t < self.t_end

    def state(self, t):
        """(center, angle) at story time t."""
        if self.kind == "throw":
            if t < self.td:
                u = (t - self.t0) / (self.td - self.t0)
                c = (self.c0[0] + (self.D[0] - self.c0[0]) * u, self.c0[1] + (self.D[1] - self.c0[1]) * u)
                return c, self.a0 + (self.ad - self.a0) * u
            s = min(t, self.tc) - self.td
            T = self.tc - self.td
            c = (self.D[0] + self.v0[0] * s, self.D[1] + self.v0[1] * s - 0.5 * G * s * s)
            u = s / T
            return c, self.ad + (self.ac - self.ad) * (1 - (1 - u) ** 1.6)
        s = min(t, self.tl) - self.t0
        T = self.tl - self.t0
        c = (self.c0[0] + self.v0[0] * s, self.c0[1] + self.v0[1] * s - 0.5 * G * s * s)
        u = s / T
        return c, self.a0 + (self.al - self.a0) * (1 - (1 - u) ** 1.4)

    def points(self, t):
        (cx, cy), a = self.state(t)
        ux, uy = math.sin(math.radians(a)), math.cos(math.radians(a))
        S, h = self.S, (self.bl + 12) * self.S
        half = self.bl * S / 2
        guard = (cx - ux * half, cy - uy * half)
        tip = (cx + ux * half, cy + uy * half)
        hilt0 = (guard[0] - ux * 20 * S, guard[1] - uy * 20 * S)
        return dict(hilt0=hilt0, guard=guard, tip=tip, sw_dir=(ux, uy), size=S, facing=1,
                    mid=((guard[0] + hilt0[0]) / 2, (guard[1] + hilt0[1]) / 2), h=h)


# ---------------------------------------------------------------- chain sim
class ChainSim:
    def __init__(self, f, who, ev, end):
        self.f = f
        self.who = who
        st = f.tracks[who][1]
        self.st = st
        self.S = st.get("size", 1.0)
        self.Lh = st.get("hold_len", 62) * self.S
        self.nf, self.nh = 26, 9
        self.drives = sorted([(t, kw) for t, k, kw in ev if k == "chain"], key=lambda e: e[0])
        self.loose = f.loose
        n = int((end + 0.6) / DT) + 2
        self.ts = np.arange(n) * DT
        self.F = np.zeros((n, self.nf, 2))
        self.Hd = np.zeros((n, self.nh, 2))
        self.drv = np.zeros(n, bool)
        self.att = [None] * n
        self._run()

    # -- target of the driven weight
    def _wp(self, w, t, t0=None):
        if w[0] == "Jf":    # where that joint was when the throw started (a miss)
            _, who, key, dx, dy = w
            J = self.f.joints_raw(who, t0)
            return (J[key][0] + dx * J["facing"], J[key][1] + dy)
        if w[0] == "J":
            _, who, key, dx, dy = w
            J = self.f.joints_raw(who, t)
            return (J[key][0] + dx * J["facing"], J[key][1] + dy)
        if w[0] == "L":   # point on a loose sword
            ls = self.loose[w[1]]
            P = ls.points(t)
            return P[w[2]]
        return w

    def _drive(self, t, J, wpos, state):
        """Returns (target or None, attach info)."""
        cur = None
        for t0, kw in self.drives:
            if t0 <= t:
                cur = (t0, kw)
        if cur is None:
            return None, None
        t0, kw = cur
        m = kw["mode"]
        dur = kw.get("dur", 0.3)
        if m == "free":
            return None, None
        if (t0, id(kw)) != state.get("key"):
            state["key"] = (t0, id(kw))
            state["start"] = tuple(wpos)
            state["th"] = None
        if m == "spin":
            if t > t0 + dur:
                return None, None
            fx = J["facing"]
            cdx, cdy = kw.get("c", (0, 0))
            hx, hy = J["hab"]
            c = (hx + cdx * fx, hy + cdy)
            r = kw.get("r", 60) * self.S
            flat = 0.27 if kw.get("plane", "side") == "over" else kw.get("flat", 1.0)
            if state["th"] is None:
                state["th"] = math.atan2((wpos[1] - c[1]) / flat, (wpos[0] - c[0]) * fx)
            sp = kw.get("turns", 2.5) * 2 * math.pi
            e_ = t - t0
            ph = e_ - 0.125 if e_ > 0.25 else e_ * e_ / 0.5     # spins up over 0.25 s
            th = state["th"] + sp * ph * kw.get("dir", 1)
            p = (c[0] + r * math.cos(th) * fx, c[1] + r * flat * math.sin(th))
            b = _smooth((t - t0) / 0.14)
            s = state["start"]
            return (s[0] + (p[0] - s[0]) * b, s[1] + (p[1] - s[1]) * b), None
        if m == "path":
            if t > t0 + dur and not kw.get("hold"):
                return None, None
            pts = [state["start"]] + [self._wp(w, t, t0 + kw.get("lead", 0.0)) for w in kw["pts"]]
            u = _ease(kw.get("ease", "out"), min(1.0, (t - t0) / dur))
            nseg = len(pts) - 1
            x = u * nseg
            i = min(nseg - 1, int(x))
            v = x - i
            P = [pts[max(0, i - 1)], pts[i], pts[i + 1], pts[min(nseg, i + 2)]]
            return _cr(*P, v), None
        if m == "attach":
            if t > t0 + dur:
                return None, None
            who, a, b, u = kw["to"]
            JJ = self.f.joints_raw(who, t)
            K = sword_view(JJ, kw.get("second", False))
            pa, pb = K[a], K[b]
            pt = (pa[0] + (pb[0] - pa[0]) * u, pa[1] + (pb[1] - pa[1]) * u)
            bl = _smooth((t - t0) / kw.get("blend", 0.001))
            s = state["start"]
            return (s[0] + (pt[0] - s[0]) * bl, s[1] + (pt[1] - s[1]) * bl), (pt, pa, pb)
        if m == "loose":
            if t > t0 + dur:
                return None, None
            P = self.loose[kw["sword"]].points(t)
            pt = P["mid"]
            return pt, (pt, P["hilt0"], P["guard"])
        return None, None

    def _run(self):
        f, who = self.f, self.who
        J0 = f.joints_raw(who, 0.0)
        h = np.array(J0["hab"], float)
        reel = J0["p"].get("reel", 70) * self.S
        x = np.array([h + (0, -reel * k / (self.nf - 1)) for k in range(self.nf)])
        x[:, 1] = np.maximum(x[:, 1], 1.5)
        xp = x.copy()
        a = np.array(J0["hilt0"], float)
        hx = np.array([a + (h - a) * k / (self.nh - 1) for k in range(self.nh)])
        hx[1:-1, 1] -= 10
        hxp = hx.copy()
        state = {}
        Lcur = reel
        inv = np.ones(self.nf)
        inv[-1] = 0.35
        for i, t in enumerate(self.ts):
            J = f.joints_raw(who, t)
            hand = np.array(J["hab"], float)
            reel = J["p"].get("reel", 70) * self.S
            tgt, att = self._drive(t, J, x[-1], state)
            # verlet step (free chain)
            v = (x - xp) * 0.988
            xp = x.copy()
            x = x + v
            x[:, 1] -= G * DT * DT
            x[0] = hand
            if tgt is not None:
                x[-1] = tgt
                d = math.dist(hand, tgt)
                Lcur = max(reel, d * 1.03)
            else:
                Lcur += (reel - Lcur) * min(1.0, DT / 0.18)
            seg = Lcur / (self.nf - 1)
            for _ in range(30):
                d = x[1:] - x[:-1]
                L = np.maximum(1e-6, np.hypot(d[:, 0], d[:, 1]))
                over = np.maximum(0.0, L - seg) / L
                w0, w1 = inv[:-1], inv[1:]
                ws = w0 + w1
                corr = d * (over / ws)[:, None]
                x[:-1] += corr * w0[:, None]
                x[1:] -= corr * w1[:, None]
                x[0] = hand
                if tgt is not None:
                    x[-1] = tgt
            gnd = x[:, 1] < 1.5
            if gnd.any():
                x[gnd, 1] = 1.5
                xp[gnd, 0] += (x[gnd, 0] - xp[gnd, 0]) * 0.25
                xp[gnd, 1] = np.minimum(xp[gnd, 1], 1.5)
            # held loop
            a = np.array(J["hilt0"], float)
            hv = (hx - hxp) * 0.99
            hxp = hx.copy()
            hx = hx + hv
            hx[:, 1] -= G * DT * DT
            hseg = self.Lh / (self.nh - 1)
            for _ in range(10):
                hx[0], hx[-1] = a, hand
                d = hx[1:] - hx[:-1]
                L = np.maximum(1e-6, np.hypot(d[:, 0], d[:, 1]))
                over = np.maximum(0.0, L - hseg) / L
                corr = d * (over * 0.5)[:, None]
                hx[:-1] += corr
                hx[1:] -= corr
            hx[0], hx[-1] = a, hand
            hx[:, 1] = np.maximum(hx[:, 1], 1.5)
            self.F[i], self.Hd[i] = x, hx
            self.drv[i] = tgt is not None
            self.att[i] = att

    def at(self, t):
        f = t / DT
        i = int(np.clip(np.floor(f), 0, len(self.ts) - 2))
        u = min(1.0, max(0.0, f - i))
        return (self.F[i] * (1 - u) + self.F[i + 1] * u,
                self.Hd[i] * (1 - u) + self.Hd[i + 1] * u, self.att[i])

    def weight(self, t):
        return tuple(self.at(t)[0][-1])

    def speed(self, t):
        return math.dist(self.weight(t), self.weight(t - 1 / 120)) * 120

    # -- drawing
    def draw(self, c, t, flat=None, J=None):
        F, Hd, att = self.at(t)
        S = self.S
        dark = flat or "#2a2d33"
        lite = flat or "#9aa3ad"
        # weight trail when it whips
        if not flat:
            sp = self.speed(t)
            if sp > 900:
                pts = [self.weight(t - k * 0.008) for k in range(12)]
                for k in range(1, len(pts)):
                    a_ = 0.45 * (1 - k / len(pts)) * min(1.0, (sp - 900) / 1200)
                    line(c, pts[k - 1], pts[k], stroke(col(self.st.get("trail", "#ffffff"), a_),
                                                       (9 - k * 0.6) * S))
        for pts in (Hd, F):
            polyline(c, [tuple(p) for p in pts], stroke(col(dark), 3.4 * S))
            polyline(c, [tuple(p) for p in pts], stroke(col(lite), 1.3 * S))
            # links: small alternating dashes
            acc = 0.0
            k = 0
            for p0, p1 in zip(pts[:-1], pts[1:]):
                L = math.dist(p0, p1)
                if L < 1e-3:
                    continue
                ux, uy = (p1[0] - p0[0]) / L, (p1[1] - p0[1]) / L
                s = (4.2 * S - acc) if acc > 0 else 0.0
                while s < L:
                    q = (p0[0] + ux * s, p0[1] + uy * s)
                    if k % 2:
                        line(c, (q[0] - uy * 2.2 * S, q[1] + ux * 2.2 * S),
                             (q[0] + uy * 2.2 * S, q[1] - ux * 2.2 * S), stroke(col(dark), 1.4 * S))
                    k += 1
                    s += 4.2 * S
                acc = L - (s - 4.2 * S)
        if att is not None:
            pt, pa, pb = att
            # coils of chain wrapped round the handle
            ux, uy = pb[0] - pa[0], pb[1] - pa[1]
            L = max(1e-3, math.hypot(ux, uy))
            ux, uy = ux / L, uy / L
            ang = math.degrees(math.atan2(uy, ux))
            for k in (-1, 0, 1):
                q = (pt[0] + ux * k * 4.2 * S, pt[1] + uy * k * 4.2 * S)
                c.save()
                c.translate(*q)
                c.rotate(ang)
                c.drawOval(skia.Rect(-2.2 * S, -5.6 * S, 2.2 * S, 5.6 * S), stroke(col(dark), 2.4 * S))
                c.restore()
        w = tuple(F[-1])
        if att is None:
            prev = tuple(F[-2])
            ux, uy = w[0] - prev[0], w[1] - prev[1]
            L = max(1e-3, math.hypot(ux, uy))
            ux, uy = ux / L, uy / L
            a0 = (w[0] - ux * 2 * S, w[1] - uy * 2 * S)
            a1 = (w[0] + ux * 9 * S, w[1] + uy * 9 * S)
            line(c, a0, a1, stroke(col(flat or "#16181c"), 9.5 * S))
            line(c, a0, a1, stroke(col(flat or "#4b525c"), 5.0 * S))
            c.drawCircle(a1[0], a1[1], 3.2 * S, fill(col(flat or "#c9a24a")))


def draw_loose(c, ls, t, flat=None):
    from draw import draw_sword
    if t < ls.t0:
        return
    P = ls.points(t)
    if ls.kind == "fling" and t >= ls.tl:
        c.save()
        c.clipRect(skia.Rect(-1e5, 0, 1e5, 1e5))
        draw_sword(c, P, flat or ls.steel, flat or "#222222", 1.0, 0, "katana")
        c.restore()
        return
    if not ls.active(t):
        return
    draw_sword(c, P, flat or ls.steel, flat or "#222222", 1.0, 0, "katana")
