"""Secondary motion for keyframed fighters.

Keyframes say where each joint angle should go. Here every angle chases its
keyed value through a damped spring, so the body overlaps and follows through
like hand animation: the head lags and bobs, the free arm swings loose, the
weapon overshoots a little at the end of a swing and settles. Hits add a kick
to the victim's spring velocities (a flinch), on top of whatever was keyed.
"""
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
    def __init__(self, track, end, impulses=(), springs=None):
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

    def sample(self, t):
        p, x = self.track.sample(t)
        f = (t - self.t0) * RATE
        i = int(np.clip(np.floor(f), 0, len(self.out) - 2))
        u = min(1.0, max(0.0, f - i))
        row = self.out[i] * (1 - u) + self.out[i + 1] * u
        for k, val in zip(ANGLE_KEYS, row):
            p[k] = float(val)
        return p, x
