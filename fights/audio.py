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


def fire_roar(rng, dur, v=1.0, burst=False):
    """Low rumbling whoosh of flame."""
    t = _t(dur)
    n = rng.standard_normal(len(t))
    s = lp(n, 420) * 1.6 + bp(n, 500, 1800) * 0.35
    flutter = 0.7 + 0.3 * np.sin(2 * np.pi * 13 * t + rng.uniform(0, 6)) * np.sin(2 * np.pi * 5 * t)
    if burst:
        env = np.exp(-4.5 * t / max(0.3, dur) * 1.0) * np.minimum(1, t / 0.008)
    else:
        env = np.sin(np.pi * np.minimum(1, t / dur)) ** 0.6
    return s * flutter * env * 0.5 * v


def icy_wind(rng, dur, v=1.0, rise=False):
    """Cold airy rush for frost creeping over the ground."""
    t = _t(dur)
    n = rng.standard_normal(len(t))
    s = bp(n, 1800, 7000) * 0.6 + bp(n, 500, 1500) * 0.5
    u = t / dur
    env = u ** 1.5 if rise else np.sin(np.pi * u) ** 0.7
    return s * env * 0.5 * v


def swell(x, dur):
    """Reverse a sample and fade it in: a suck-in that ends on the beat."""
    n = int(dur * SR)
    y = x[:n][::-1].copy()
    y *= np.linspace(0, 1, len(y)) ** 1.5
    return y


def chime(factor, dur):
    """Crystal ring made from the recorded bell, pitched and shortened."""
    x = pitch(sample("bell_heavy"), factor)
    n = min(len(x), int(dur * SR))
    return x[:n] * np.linspace(1, 0, n) ** 0.8


SFX_DIR = __import__("os").path.join(__import__("os").path.dirname(__file__), "sfx")
_CACHE = {}


def sample(name):
    """Load a CC0 recording from fights/sfx (see sfx/CREDITS.md)."""
    if name not in _CACHE:
        import subprocess
        path = f"{SFX_DIR}/{name}.ogg"
        raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar",
                              str(SR), "-f", "f32le", "-"], capture_output=True,
                             check=True).stdout
        x = np.frombuffer(raw, np.float32).astype(np.float64)
        _CACHE[name] = x / max(1e-6, np.abs(x).max())
    return _CACHE[name]


def pitch(x, factor):
    """Resample: factor > 1 = higher and shorter."""
    if abs(factor - 1) < 1e-3:
        return x
    n = int(len(x) / factor)
    return np.interp(np.arange(n) * factor, np.arange(len(x)), x)


def pick(rng, names):
    return sample(names[rng.integers(len(names))])


def mix(cues, dur, seed=7):
    """cues: list of (video_time, kind, params)."""
    rng = np.random.default_rng(seed)
    out = np.zeros(int(dur * SR) + 3 * SR)
    w = wind(rng, dur + 1)
    out[:len(w)] += 0.06 * w

    def put(t0, s, gain=1.0):
        i = int(max(0, t0) * SR)
        if i >= len(out):
            return
        s = s[:len(out) - i]
        out[i:i + len(s)] += s * gain

    RINGS = ["clash_ring_1", "clash_ring_2"]
    CLANGS = ["clang_1", "clang_2", "clang_3", "clang_4"]
    METAL = ["metal_hit_1", "metal_hit_2", "metal_hit_3", "metal_hit_4"]
    SWISH = ["swish_1", "swish_2", "swish_3", "swish_4", "swish_5"]
    HEAVY_SW = ["swoosh_heavy_1", "swoosh_heavy_2"]
    PUNCH = ["punch_heavy_0", "punch_heavy_1", "punch_heavy_2"]
    STEPS = ["step_0", "step_1", "step_2"]
    GLASS_H = ["glass_heavy_0", "glass_heavy_1", "glass_heavy_2"]
    GLASS_M = ["glass_medium_0", "glass_medium_1"]
    GLASS_L = ["glass_light_0", "glass_light_1"]
    for t0, kind, kw in cues:
        v = kw.get("v", 1.0)
        r = rng.uniform(0.94, 1.06)
        if kind == "swoosh":
            if kw.get("heavy"):
                put(t0 - 0.05, pitch(pick(rng, HEAVY_SW), 0.75 * r), 0.9 * v)
            else:
                put(t0 - 0.03, pitch(pick(rng, SWISH), 1.15 * r), 0.75 * v)
        elif kind == "zip":
            put(t0, pitch(pick(rng, SWISH), 1.5 * r), 0.8 * v)
            put(t0, swoosh(rng, 0.16, 0.6 * v, 1.8))
        elif kind == "clash":
            big = kw.get("big", False)
            put(t0, pitch(pick(rng, RINGS), (0.85 if big else 1.0) * r), 0.9 * v)
            put(t0, pitch(pick(rng, METAL), r), 0.6 * v)
            if big:
                put(t0, pitch(pick(rng, PUNCH), 0.8), 0.9 * v)
                put(t0, pitch(sample("metal_heavy_1"), 0.8), 0.6 * v)
                put(t0, ground(rng, 0.5 * v))
            if kw.get("final"):
                put(t0, iai(rng, 0.8))
        elif kind == "hit":
            put(t0, pitch(pick(rng, CLANGS), 1.1 * r), 0.55 * v)
            put(t0, pitch(pick(rng, SWISH), 1.6 * r), 0.5 * v)
            put(t0, pitch(pick(rng, PUNCH), 1.2 * r), 0.35 * v)
        elif kind == "decap":
            put(t0, pitch(pick(rng, SWISH), 0.9), 1.0)
            put(t0, pitch(pick(rng, RINGS), 0.7), 0.5)
            put(t0, ground(rng, 0.6))
        elif kind == "dmg":
            put(t0, pitch(sample(f"blunt_{rng.integers(1, 5)}"), 0.85 * r), 0.9)
            put(t0, pitch(pick(rng, PUNCH), 0.9 * r), 0.8)
        elif kind == "slam":
            put(t0, pitch(sample("soft_heavy"), 0.8), 1.0 * v)
            put(t0, pitch(pick(rng, PUNCH), 0.7), 1.0 * v)
            put(t0, pitch(sample("metal_heavy_0"), 0.7), 0.6 * v)
            put(t0, ground(rng, 1.3 * v))
        elif kind == "stomp":
            put(t0, pitch(pick(rng, STEPS), 0.6 * r), 0.9 * v)
            put(t0, drum(rng, 0.7 * v))
        elif kind in ("step",):
            put(t0, pitch(pick(rng, STEPS), r), 0.5 * v)
        elif kind in ("skid", "gust"):
            put(t0, bp(rng.standard_normal(int(0.35 * SR)), 300, 2500)
                * np.exp(-8 * _t(0.35)) * 0.4 * v)
            put(t0, pitch(pick(rng, STEPS), 0.9 * r), 0.5 * v)
        elif kind == "thud":
            put(t0, pitch(pick(rng, PUNCH), 0.8 * r), 0.9 * v)
            put(t0, thud(rng, 0.6 * v))
        elif kind == "break":
            put(t0, pitch(sample("metal_latch"), 1.2), 0.9)
            put(t0, pitch(pick(rng, RINGS), 1.5), 0.5)
        elif kind == "draw":
            put(t0, sample("unsheathe"), 0.8 * v)
        elif kind == "sheathe":
            put(t0, sample("metal_click"), 0.8 * v)
        elif kind == "twinkle":
            tt = _t(0.8)
            put(t0, (np.sin(2 * np.pi * 2637 * tt) + 0.6 * np.sin(2 * np.pi * 3951 * tt))
                * np.exp(-5 * tt) * 0.35)
        elif kind == "ground":
            put(t0, ground(rng, v))
        elif kind == "drum":
            put(t0, drum(rng, v))
        elif kind == "heart":
            put(t0, heart(rng, v))
        elif kind == "iai":
            put(t0, iai(rng, v))
        elif kind == "riser":
            put(t0, riser(rng, kw["dur"]))
        elif kind == "el_fireball":
            put(t0 - 0.03, pitch(pick(rng, HEAVY_SW), 0.6 * r), 0.8 * v)
            put(t0, fire_roar(rng, 0.35, 0.7 * v))
        elif kind == "el_firehit":
            put(t0, pitch(pick(rng, PUNCH), 0.75 * r), 0.9 * v)
            put(t0, fire_roar(rng, 0.45, 0.9 * v, burst=True))
        elif kind == "el_explode":
            put(t0, pitch(sample("soft_heavy"), 0.7), 1.0 * v)
            put(t0, pitch(pick(rng, PUNCH), 0.6), 1.0 * v)
            put(t0, ground(rng, 1.4 * v))
            put(t0, fire_roar(rng, 1.4, 1.2 * v, burst=True))
        elif kind == "el_roar":
            put(t0, fire_roar(rng, kw.get("dur", 1.0), 0.6 * v))
        elif kind == "el_iceform":
            # swell in, hard crack, deep thump, crystal ring
            sw = swell(pitch(pick(rng, GLASS_M), 0.8 * r), 0.18)
            put(t0 - 0.18, sw, 0.5 * v)
            put(t0, pitch(pick(rng, GLASS_H), 1.25 * r), 0.9 * v)
            put(t0, pitch(sample("soft_heavy"), 0.85), 0.9 * v)
            put(t0, pitch(pick(rng, PUNCH), 0.8 * r), 0.6 * v)
            put(t0 + 0.01, chime(2.0 * r, 0.5), 0.3 * v)
        elif kind == "el_icebreak":
            put(t0, pitch(pick(rng, GLASS_H), 0.62 * r), 1.0 * v)
            put(t0, pitch(pick(rng, GLASS_H), 1.0 * r), 0.9 * v)
            put(t0, pitch(pick(rng, PUNCH), 0.6), 0.9 * v)
            put(t0, ground(rng, 0.7 * v))
            for dl in (0.09, 0.19, 0.33, 0.5):   # pieces raining down
                put(t0 + dl * rng.uniform(0.8, 1.2),
                    pitch(pick(rng, GLASS_L + GLASS_M), rng.uniform(1.0, 1.6)), 0.35 * v)
        elif kind == "el_shard":
            put(t0 - 0.02, pitch(pick(rng, SWISH), 1.35 * r), 0.9 * v)
            put(t0 - 0.02, pitch(pick(rng, HEAVY_SW), 1.3 * r), 0.4 * v)
            put(t0, chime(3.0 * r, 0.25), 0.3 * v)
        elif kind == "el_icehit":
            put(t0, pitch(pick(rng, PUNCH), 0.85 * r), 1.0 * v)
            put(t0, pitch(sample(f"blunt_{rng.integers(1, 5)}"), 0.9 * r), 0.6 * v)
            put(t0, pitch(pick(rng, GLASS_H), 1.15 * r), 0.8 * v)
            put(t0 + 0.06, pitch(pick(rng, GLASS_L), 1.4 * r), 0.3 * v)
        elif kind == "el_steam":
            n = int(0.9 * SR)
            tt = np.arange(n) / SR
            put(t0, hp(rng.standard_normal(n), 3500) * np.exp(-4 * tt) * 0.35 * v)
        elif kind == "el_frost":
            d_ = max(0.1, kw.get("dur", 0.5))
            put(t0, icy_wind(rng, d_ + 0.25, 0.7 * v))
            for i in range(max(1, int(d_ * 9))):
                put(t0 + rng.uniform(0, d_), pitch(pick(rng, GLASS_L), rng.uniform(1.5, 2.2)),
                    0.18 * v)
        elif kind == "el_freeze":
            d_ = max(0.1, kw.get("dur", 0.5))
            put(t0, icy_wind(rng, d_ + 0.1, 1.0 * v, rise=True))
            put(t0, swell(chime(1.5, 1.2), d_), 0.6 * v)
            for i in range(6):
                put(t0 + d_ * i / 6, pitch(pick(rng, GLASS_M), 1.2 + 0.1 * i), 0.3 * v)
            # locked solid: heavy crack with a long cold ring
            put(t0 + d_, pitch(pick(rng, GLASS_H), 0.6), 1.0 * v)
            put(t0 + d_, pitch(sample("soft_heavy"), 0.7), 1.0 * v)
            put(t0 + d_, pitch(pick(rng, PUNCH), 0.65), 0.9 * v)
            put(t0 + d_, chime(0.75, 1.8), 0.5 * v)
            put(t0 + d_, chime(1.5, 1.2), 0.3 * v)
        elif kind == "el_rumble":
            d_ = kw.get("dur", 1.0)
            tt = _t(d_)
            put(t0, lp(rng.standard_normal(len(tt)), 120) * (tt / d_) ** 1.5 * 2.2 * v)
            for i in range(int(d_ * 7)):     # cracks coming faster and louder
                u = (i / max(1, int(d_ * 7) - 1)) ** 0.7
                put(t0 + d_ * u, pitch(pick(rng, GLASS_M + GLASS_H), rng.uniform(0.9, 1.4)),
                    (0.2 + 0.5 * u) * v)
            put(t0, riser(rng, d_) * 0.8)
    out = out[:int(dur * SR)]
    out /= max(1e-6, np.abs(out).max()) / 0.9
    return np.stack([out, out], axis=1).astype(np.float32)
