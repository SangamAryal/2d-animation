"""Foot planting for fluid fights (07+).

Keyframed stick figures skate: every key moves the hip and both feet slide
along with it. Here each foot sticks to the ground while it carries weight,
and when the posed foot has drifted too far from where it is planted the foot
takes a quick arcing step to catch up. Leaving the ground (jumps, kicks, flips,
fast dashes) releases the foot and it eases back onto the posed position, so
nothing ever pops. Legs are then re-solved with two-bone IK in rig.leg_ik.
"""
import math

import numpy as np

from rig import FOOT_R, leg_ik, leg_ik_drawn

RATE = 240


def _smooth(u):
    u = min(1.0, max(0.0, u))
    return u * u * (3 - 2 * u)


class Planter:
    def __init__(self, raw, end, size=1.0, drawn=False):
        self.ik = leg_ik_drawn if drawn else leg_ik
        """raw(t) -> joints dict without foot fixes."""
        self.raw = raw
        self.t0 = -0.5
        n = int((end + 1.2 - self.t0) * RATE) + 2
        self.n = n
        dt = 1.0 / RATE
        S = size
        thr = 15.0 * S
        out = {s: np.zeros((n, 2)) for s in "fb"}
        use = {s: np.zeros(n, bool) for s in "fb"}
        st = {s: dict(mode="free", P=None, off=(0.0, 0.0), ts=0, te=0, frm=None) for s in "fb"}
        prev_hip = None
        for i in range(n):
            t = self.t0 + i * dt
            J = raw(t)
            p = J["p"]
            hip = J["hip"]
            vx = 0.0 if prev_hip is None else (hip[0] - prev_hip[0]) / dt
            prev_hip = hip
            r = ((p.get("rot", 0) + 180) % 360) - 180
            body_ok = abs(r) < 30 and abs(vx) < 1500 and p.get("hidden", 0) < 0.5
            for s in "fb":
                o = "b" if s == "f" else "f"
                f = J["ft" + s]
                contact = body_ok and f[1] <= FOOT_R + 5 * S
                q = st[s]
                if not contact:
                    if q["mode"] != "free":
                        cur = out[s][i - 1] if i else f
                        q["off"] = (cur[0] - f[0], cur[1] - f[1])
                        q["mode"] = "free"
                    k = math.exp(-dt * 26)
                    q["off"] = (q["off"][0] * k, q["off"][1] * k)
                    pos = (f[0] + q["off"][0], f[1] + q["off"][1])
                elif q["mode"] == "free":
                    pos = (f[0] + q["off"][0], f[1])
                    q["mode"], q["P"] = "plant", pos
                elif q["mode"] == "plant":
                    pos = q["P"]
                    dlt = f[0] - pos[0]
                    other_step = st[o]["mode"] == "step"
                    if abs(dlt) > thr and (not other_step or abs(dlt) > 2.4 * thr):
                        dur = min(0.15, max(0.075, 0.07 + abs(dlt) / 2400))
                        q.update(mode="step", ts=t, te=t + dur, frm=pos)
                if q["mode"] == "step":
                    u = (t - q["ts"]) / (q["te"] - q["ts"])
                    T = raw(q["te"])["ft" + s]
                    tgt = (T[0], min(f[1], FOOT_R + 1))
                    e = _smooth(u)
                    dxs = tgt[0] - q["frm"][0]
                    h = min(16.0, 3.0 + abs(dxs) * 0.28) * S
                    pos = (q["frm"][0] + dxs * e,
                           q["frm"][1] + (tgt[1] - q["frm"][1]) * e + math.sin(math.pi * min(1, u)) * h)
                    if u >= 1:
                        q["mode"], q["P"] = "plant", tgt
                        pos = tgt
                out[s][i] = pos
                use[s][i] = q["mode"] != "free" or abs(q["off"][0]) + abs(q["off"][1]) > 0.05
        self.out, self.use = out, use

    def apply(self, J, t):
        f = (t - self.t0) * RATE
        i = int(min(max(math.floor(f), 0), self.n - 2))
        u = min(1.0, max(0.0, f - i))
        for s in "fb":
            if not (self.use[s][i] or self.use[s][i + 1]):
                continue
            a, b = self.out[s][i], self.out[s][i + 1]
            self.ik(J, s, (a[0] + (b[0] - a[0]) * u, a[1] + (b[1] - a[1]) * u))
        return J
