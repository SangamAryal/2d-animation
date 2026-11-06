"""Code-made sound effects for the fight videos (no samples, $0)."""
import numpy as np
from scipy.signal import butter, sosfilt

SR = 48000


def _t(dur):
    return np.arange(int(dur * SR)) / SR


def bp(x, lo, hi, order=2):
    sos = butter(order, [lo, hi], btype="band", fs=SR, output="sos")
    return sosfilt(sos, x)


def lp(x, f, order=2):
    return sosfilt(butter(order, f, btype="low", fs=SR, output="sos"), x)


def hp(x, f, order=2):
    return sosfilt(butter(order, f, btype="high", fs=SR, output="sos"), x)


def swoosh(rng, dur=0.26, v=1.0, pitch=1.0):
    t = _t(dur)
    n = rng.standard_normal(len(t))
    # sweep a band through the noise in short blocks
    out = np.zeros_like(n)
    blocks = 12
    for i in range(blocks):
        a, b = i * len(t) // blocks, (i + 1) * len(t) // blocks
        u = i / (blocks - 1)
        fc = (700 + 2600 * np.sin(np.pi * u)) * pitch
        seg = bp(n[max(0, a - 400):b], fc * 0.6, min(fc * 1.6, 20000))
        out[a:b] = seg[-(b - a):]
    env = np.sin(np.pi * np.clip(t / dur, 0, 1)) ** 1.5
    return out * env * 0.55 * v


def clang(rng, v=1.0, big=False):
    dur = 1.6 if big else 1.0
    t = _t(dur)
    f0 = rng.uniform(1150, 1500) * (0.8 if big else 1.0)
    out = np.zeros_like(t)
    for ratio, amp, dec in [(1, 1.0, 3.0), (2.76, 0.6, 5.0), (5.40, 0.4, 8.0),
                            (8.93, 0.25, 12.0), (1.5, 0.3, 4.0)]:
        f = f0 * ratio * rng.uniform(0.99, 1.01)
        out += amp * np.sin(2 * np.pi * f * t + rng.uniform(0, 6)) * np.exp(-dec * t)
    click = hp(rng.standard_normal(len(t)), 2500) * np.exp(-60 * t)
    thump = np.sin(2 * np.pi * (120 * np.exp(-8 * t)) * t) * np.exp(-12 * t)
    s = 0.35 * out + 0.9 * click + (0.8 if big else 0.4) * thump
    return s * v * 0.7


def hit(rng, v=1.0):
    t = _t(0.45)
    f = 95 * np.exp(-5 * t) + 40
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-9 * t)
    crack = lp(rng.standard_normal(len(t)), 1800) * np.exp(-35 * t)
    return (1.1 * body + 0.9 * crack) * v * 0.8


def ground(rng, v=1.0):
    t = _t(1.2)
    f = 70 * np.exp(-3 * t) + 30
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-5 * t)
    rumble = lp(rng.standard_normal(len(t)), 300) * np.exp(-3.5 * t)
    debris = bp(rng.standard_normal(len(t)), 1500, 5000) * np.exp(-14 * t)
    return (1.2 * body + 1.4 * rumble + 0.35 * debris) * v * 0.7


def step(rng, v=1.0):
    t = _t(0.09)
    s = lp(rng.standard_normal(len(t)), 900) * np.exp(-45 * t)
    s += 0.5 * np.sin(2 * np.pi * 110 * t) * np.exp(-40 * t)
    return s * v * 0.5


def thud(rng, v=1.0):
    t = _t(0.5)
    s = np.sin(2 * np.pi * (80 * np.exp(-4 * t) + 35) * t) * np.exp(-8 * t)
    s += 0.6 * lp(rng.standard_normal(len(t)), 500) * np.exp(-12 * t)
    return s * v * 0.8


def draw_scrape(rng, v=1.0):
    t = _t(0.42)
    scrape = bp(rng.standard_normal(len(t)), 3000, 9000) * np.minimum(1, t / 0.3) \
        * np.exp(-2 * t)
    ring = np.sin(2 * np.pi * 3400 * t) * np.exp(-6 * np.maximum(0, t - 0.3)) \
        * (t > 0.3)
    return (0.35 * scrape + 0.25 * ring) * v


def sheathe(rng, v=1.0, final=False):
    t = _t(0.9 if final else 0.5)
    slide = bp(rng.standard_normal(len(t)), 2500, 7000) * np.exp(-9 * t) * 0.25
    k = (t > 0.14).astype(float)
    tc = np.maximum(0, t - 0.14)
    click = hp(rng.standard_normal(len(t)), 3000) * np.exp(-200 * tc) * k
    ting = np.sin(2 * np.pi * 4200 * t) * np.exp(-5 * tc) * k * (0.25 if final else 0.1)
    return (slide + click + ting) * v


def drum(rng, v=1.0):
    t = _t(1.0)
    f = 62 * np.exp(-2.5 * t) + 48
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-4 * t)
    s += 0.4 * lp(rng.standard_normal(len(t)), 400) * np.exp(-25 * t)
    return s * v * 0.9


def heart(rng, v=1.0):
    t = _t(0.55)
    def beat(t0):
        tt = np.maximum(0, t - t0)
        return np.sin(2 * np.pi * 55 * tt) * np.exp(-14 * tt) * (t >= t0)
    return (beat(0) + 0.7 * beat(0.22)) * v * 0.9


def iai(rng, v=1.0):
    """The quick-draw: whoosh, a sharp ring, then a deep boom."""
    t = _t(2.4)
    w = np.zeros_like(t)
    sw = swoosh(rng, 0.22, 1.4, 1.5)
    w[:len(sw)] += sw
    shing = np.zeros_like(t)
    for f, a in [(5200, 0.5), (7900, 0.3), (2600, 0.3)]:
        shing += a * np.sin(2 * np.pi * f * t) * np.exp(-3 * t)
    boom = np.sin(2 * np.pi * (55 * np.exp(-1.5 * t) + 28) * t) * np.exp(-2 * t)
    return (w + 0.45 * shing + 1.0 * boom) * v


def snap(rng, v=1.0):
    t = _t(0.6)
    crack = hp(rng.standard_normal(len(t)), 2000) * np.exp(-50 * t)
    ring = np.sin(2 * np.pi * 2900 * t) * np.exp(-7 * t) * 0.3
    return (crack + ring) * v * 0.6


def wind(rng, dur):
    n = rng.standard_normal(int(dur * SR))
    n = lp(n, 500)
    t = np.arange(len(n)) / SR
    mod = 0.6 + 0.4 * np.sin(2 * np.pi * 0.17 * t) * np.sin(2 * np.pi * 0.05 * t + 1)
    return n * mod * 0.6


def riser(rng, dur):
    t = _t(dur)
    f = 200 + 900 * (t / dur) ** 2
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / dur) ** 2
    s += bp(rng.standard_normal(len(t)), 2000, 6000) * (t / dur) ** 3 * 0.5
    return s * 0.3


def mix(cues, dur, seed=7):
    """cues: list of (video_time, kind, params)."""
    rng = np.random.default_rng(seed)
    out = np.zeros(int(dur * SR) + SR)
    w = wind(rng, dur + 1)
    out[:len(w)] += 0.08 * w

    def put(t0, s, gain=1.0):
        i = int(t0 * SR)
        if i >= len(out):
            return
        s = s[:len(out) - i]
        out[i:i + len(s)] += s * gain

    for t0, kind, kw in cues:
        v = kw.get("v", 1.0)
        if kind == "swoosh":
            put(t0, swoosh(rng, kw.get("dur", 0.26), v, kw.get("pitch", 1.0)))
        elif kind == "clash":
            put(t0, clang(rng, v, kw.get("big", False)))
        elif kind == "hit":
            put(t0, hit(rng, v))
        elif kind == "ground":
            put(t0, ground(rng, v))
        elif kind == "step":
            put(t0, step(rng, v))
        elif kind == "thud":
            put(t0, thud(rng, v))
        elif kind == "draw":
            put(t0, draw_scrape(rng, v))
        elif kind == "sheathe":
            put(t0, sheathe(rng, v, kw.get("final", False)))
        elif kind == "drum":
            put(t0, drum(rng, v))
        elif kind == "heart":
            put(t0, heart(rng, v))
        elif kind == "iai":
            put(t0, iai(rng, v))
        elif kind == "snap":
            put(t0, snap(rng, v))
        elif kind == "riser":
            put(t0, riser(rng, kw["dur"]))
    out = out[:int(dur * SR)]
    out /= max(1e-6, np.abs(out).max()) / 0.9
    return np.stack([out, out], axis=1).astype(np.float32)
