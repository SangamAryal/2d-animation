"""Secondary motion for keyframed fighters.

Keyframes say where each joint angle should go. Here every angle chases its
keyed value through a damped spring, so the body overlaps and follows through
like hand animation: the head lags and bobs, the free arm swings loose, the
weapon overshoots a little at the end of a swing and settles. Hits add a kick
to the victim's spring velocities (a flinch), on top of whatever was keyed.
"""
import math

import numpy as np

from rig import ANGLE_KEYS

RATE = 600  # simulation steps per animation second

# (natural frequency rad/s, damping ratio) per angle key
SPRINGS = {
    "T": (46, 0.62), "H": (30, 0.42),
    "uaf": (78, 0.78), "faf": (70, 0.72),
    "uab": (30, 0.48), "fab": (26, 0.42),
    "thf": (95, 0.95), "shf": (95, 0.95), "thb": (95, 0.95), "shb": (95, 0.95),
    "sw": (82, 0.55),
}


class Smoothed:
    def __init__(self, track, end, impulses=(), springs=None, fluid=False):
        sp = dict(SPRINGS)
        sp.update(springs or {})
        self.track = track
        n = int((end + 1.0) * RATE) + 2
        self.t0 = -0.5
        ts = self.t0 + np.arange(n) / RATE
        tgt = np.zeros((n, len(ANGLE_KEYS)))
        for i, t in enumerate(ts):
            p, _ = track.sample(t)
            tgt[i] = [p[k] for k in ANGLE_KEYS]
        w = np.array([sp[k][0] for k in ANGLE_KEYS], float)
        z = np.array([sp[k][1] for k in ANGLE_KEYS], float)
        kick = np.zeros_like(tgt)
        for t, dv in impulses:
            i = int((t - self.t0) * RATE)
            if 0 <= i < n:
                for k, v in dv.items():
                    kick[i, ANGLE_KEYS.index(k)] += v
        out = np.zeros_like(tgt)
        x = tgt[0].copy()
        v = np.zeros_like(x)
        dt = 1.0 / RATE
        for i in range(n):
            v += kick[i]
            a = w * w * (tgt[i] - x) - 2 * z * w * v
            v += a * dt
            x += v * dt
            out[i] = x
        self.out = out
        self.fluid = fluid
        if fluid:
            self._root(track, ts, end)

    def _root(self, track, ts, end):
        """Fluid mode (fight 07+): the hips travel on springs too, so moves
        flow through keys in arcs instead of stopping dead at each one, and a
        squash/stretch value rides on top of them."""
        n = len(ts)
        xs = np.zeros(n)
        lift = np.zeros(n)
        sqk = np.zeros(n)
        for i, t in enumerate(ts):
            p, x = track.sample(t)
            xs[i] = x
            lift[i] = p["air"] + p["dy"]
            sqk[i] = p.get("sq", 0.0)
        dt = 1.0 / RATE
        # x: fast enough to keep snaps snappy, a little overshoot to settle
        ox, ol, osq = np.zeros(n), np.zeros(n), np.zeros(n)
        x, vx, l, vl, q, vq = xs[0], 0.0, lift[0], 0.0, 0.0, 0.0
        wx, zx, wl, zl, wq, zq = 44.0, 0.74, 40.0, 0.80, 34.0, 0.32
        for i in range(n):
            ax = wx * wx * (xs[i] - x) - 2 * zx * wx * vx
            vx += ax * dt
            x += vx * dt
            al = wl * wl * (lift[i] - l) - 2 * zl * wl * vl
            l_prev = l
            vl += al * dt
            l += vl * dt
            # landing: coming down fast through the ground line squashes the body
            if l_prev >= 4 > l and vl < -250:
                vq -= min(5.0, -vl / 220.0)
            # target: keyed squash + stretch along fast travel
            spd = math.hypot(vx, vl)
            tq = sqk[i] + min(0.16, max(0.0, (spd - 500) / 9000))
            aq = wq * wq * (tq - q) - 2 * zq * wq * vq
            vq += aq * dt
            q += vq * dt
            ox[i], ol[i], osq[i] = x, l, max(-0.3, min(0.3, q))
        self.rx, self.rl, self.rsq, self.rlift = ox, ol, osq, lift

    def sample(self, t):
        p, x = self.track.sample(t)
        f = (t - self.t0) * RATE
        i = int(np.clip(np.floor(f), 0, len(self.out) - 2))
        u = min(1.0, max(0.0, f - i))
        row = self.out[i] * (1 - u) + self.out[i + 1] * u
        for k, val in zip(ANGLE_KEYS, row):
            p[k] = float(val)
        if self.fluid:
            def at(a):
                return float(a[i] * (1 - u) + a[i + 1] * u)
            x = at(self.rx)
            # keep the keyed split between air and dy, but use the smoothed sum
            p["dy"] += at(self.rl) - at(self.rlift)
            p["sq"] = at(self.rsq)
        return p, x
