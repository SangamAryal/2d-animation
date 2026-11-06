"""Synthesized soundtrack for a sim: blade cuts, early wall taps, a soft pad and a finale.

Everything is generated with numpy, so there are no samples and no licensing questions.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000
# A minor pentatonic over three octaves; generation g climbs the scale.
PENTA = [0, 3, 5, 7, 10]


def note_freq(step: int, base: float = 440.0) -> float:
    octave, k = divmod(step, len(PENTA))
    return base * 2 ** ((PENTA[k] + 12 * octave) / 12)


def shing(freq: float, dur: float = 0.45, rng=None) -> np.ndarray:
    """Short metallic 'ting' with a bright noise transient."""
    t = np.arange(int(dur * SR)) / SR
    out = np.zeros_like(t)
    for ratio, amp, dec in [(1.0, 1.0, 7), (2.76, 0.5, 11), (5.40, 0.25, 16), (8.93, 0.12, 24)]:
        f = freq * ratio * (1 + (rng.normal() * 0.003 if rng is not None else 0))
        out += amp * np.sin(2 * math.pi * f * t) * np.exp(-dec * t)
    noise = (rng.standard_normal(len(t)) if rng is not None else np.random.standard_normal(len(t)))
    sos = butter(2, 5000, "hp", fs=SR, output="sos")
    out += 0.2 * sosfilt(sos, noise) * np.exp(-60 * t)
    attack = np.minimum(1, t / 0.002)
    return out * attack


def tap(dur=0.12) -> np.ndarray:
    t = np.arange(int(dur * SR)) / SR
    return np.sin(2 * math.pi * 180 * t * (1 - 0.4 * t / dur)) * np.exp(-40 * t)


def plink(freq: float, rng, dur: float = 0.16) -> np.ndarray:
    """Small glassy ball 'tik': a quick sine + overtone with a soft click."""
    t = np.arange(int(dur * SR)) / SR
    f = freq * (1 + rng.normal() * 0.01)
    out = np.sin(2 * math.pi * f * t) * np.exp(-38 * t) + 0.35 * np.sin(2 * math.pi * 2.9 * f * t) * np.exp(-60 * t)
    click = rng.standard_normal(len(t)) * np.exp(-900 * t) * 0.25
    return (out + click) * np.minimum(1, t / 0.0015)


def pad(seconds: float, chord=(220.0, 261.63, 329.63, 392.0)) -> np.ndarray:
    t = np.arange(int(seconds * SR)) / SR
    out = np.zeros_like(t)
    for i, f in enumerate(chord):
        lfo = 1 + 0.002 * np.sin(2 * math.pi * (0.1 + 0.03 * i) * t)
        out += np.sin(2 * math.pi * f * lfo * t) + 0.3 * np.sin(2 * math.pi * 2 * f * t)
    sos = butter(2, 1200, "lp", fs=SR, output="sos")
    return sosfilt(sos, out) / len(chord)


def add(buf: np.ndarray, clip: np.ndarray, at: int, gain: float, pan: float = 0.0):
    if at >= buf.shape[0]:
        return
    end = min(buf.shape[0], at + len(clip))
    c = clip[: end - at] * gain
    l = math.cos((pan + 1) * math.pi / 4)
    r = math.sin((pan + 1) * math.pi / 4)
    buf[at:end, 0] += c * l
    buf[at:end, 1] += c * r


def build_audio(sim: dict, out_wav: str, note_base: float = 330.0, seed: int = 3):
    rng = np.random.default_rng(seed)
    cfg = sim["cfg"]
    fps = cfg.fps
    n_frames = len(sim["pos"])
    total = n_frames / fps + 1.5
    buf = np.zeros((int(total * SR), 2))

    # soft pad that swells as the ring fills
    p = pad(total)
    counts = np.array([len(x) for x in sim["pos"]], float)
    env_frames = 0.25 + 0.75 * np.clip(np.log2(counts + 1) / math.log2(cfg.max_balls), 0, 1)
    env = np.interp(np.arange(len(p)) / SR, np.arange(n_frames) / fps, env_frames)
    fade = np.minimum(1, np.arange(len(p)) / (1.5 * SR))
    buf[:, 0] += 0.06 * p * env * fade
    buf[:, 1] += 0.06 * p * env * fade

    # black hole: a deep rumble that grows with the hole and stays to the end
    holes = np.array(sim["hole"], float)
    if holes.max() > 0:
        tt = np.arange(len(p)) / SR
        sos = butter(2, 120, "lp", fs=SR, output="sos")
        rum = sosfilt(sos, rng.standard_normal(len(p))) * 3 + 0.5 * np.sin(2 * math.pi * 46 * tt)
        henv = np.interp(tt, np.arange(n_frames) / fps, np.clip(holes / 120.0, 0, 1))
        henv[int(n_frames / fps * SR):] = henv[int(n_frames / fps * SR) - 1]
        buf[:, 0] += 0.12 * rum * henv * fade
        buf[:, 1] += 0.12 * rum * henv * fade

    shing_cache: dict[int, np.ndarray] = {}
    tap_clip = tap()
    plinks = [plink(note_freq(s, note_base * 2), rng) for s in range(0, 10)]
    tg = np.arange(int(0.25 * SR)) / SR
    gulp = np.sin(2 * math.pi * (160 - 260 * tg) * tg) * np.exp(-14 * tg)
    for fi in range(n_frames):
        at = int(fi / fps * SR)
        cuts = sim["cuts"][fi]
        if cuts:
            # at most 3 voices per frame; loudness grows gently with the number of cuts
            k = len(cuts)
            gain = 0.32 * (1 + 0.25 * math.log2(k)) / min(k, 3)
            for (x, y, g) in cuts[:3]:
                step = int(g) + 2
                if step not in shing_cache:
                    shing_cache[step] = shing(note_freq(step, note_base), rng=rng)
                pan = max(-0.8, min(0.8, x / cfg.ring_radius))
                add(buf, shing_cache[step], at + int(rng.integers(0, SR // fps)), gain, pan)
        eats = sim["eats"][fi]
        if eats:
            add(buf, gulp, at, 0.22 * (1 + 0.2 * math.log2(len(eats))) / min(len(eats), 2))
        # ball bounces: up to 6 overlapping plinks per frame, quieter the more there are
        top, total = sim["bounces"][fi]
        if top:
            voices = top[:6]
            dens = 1.0 / math.sqrt(len(voices))
            for (vn, bx, kind) in voices:
                if kind == 1:
                    add(buf, tap_clip, at, min(0.35, vn / 2500))
                    continue
                clip = plinks[int(rng.integers(0, len(plinks)))]
                g = min(0.16, 0.03 + vn / 9000) * dens * (1 + 0.15 * math.log2(1 + total))
                pan = max(-0.8, min(0.8, bx / cfg.ring_radius))
                add(buf, clip, at + int(rng.integers(0, SR // fps)), g, pan)

    # finale when the run ends: low thump + a chord (falling if the balls lost)
    if sim["full_frame"] is not None:
        at = int(sim["full_frame"] / fps * SR)
        t = np.arange(int(2.5 * SR)) / SR
        thump = np.sin(2 * math.pi * 55 * t * (1 - 0.3 * t)) * np.exp(-3 * t)
        add(buf, thump, at, 0.5)
        steps = [15, 14, 12, 10] if sim["end_kind"] == "empty" else [10, 12, 14, 15]
        for i, step in enumerate(steps):
            add(buf, shing(note_freq(step, note_base), dur=2.0, rng=rng), at + i * 2400, 0.18, (i - 1.5) / 3)

    # fade the tail with the picture
    tail = int(0.5 * SR)
    end = int(n_frames / fps * SR)
    buf[end - tail:end] *= np.linspace(1, 0, tail)[:, None]
    buf[end:] = 0
    peak = np.abs(buf).max() or 1
    buf = buf / peak * 0.89
    wavfile.write(out_wav, SR, (buf * 32767).astype(np.int16))
