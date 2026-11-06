"""Synthesized soundtrack for volcano vs snowstorm. Never silent: a wind bed runs start to end."""
from __future__ import annotations

import math

import numpy as np
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 48000


def _env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1, t / attack) * np.exp(-decay * t), t


def hiss(rng, dur=0.45):
    n = int(dur * SR)
    e, t = _env(n, 0.01, 7)
    sos = butter(2, [3000, 9000], "bandpass", fs=SR, output="sos")
    ping = 0.25 * np.sin(2 * math.pi * 2600 * t) * np.exp(-25 * t)
    return sosfilt(sos, rng.standard_normal(n)) * e * 1.4 + ping


def blub(freq, dur=0.35):
    n = int(dur * SR)
    e, t = _env(n, 0.004, 9)
    f = freq * (1.7 - 0.9 * np.minimum(1, t / 0.12))
    ph = 2 * math.pi * np.cumsum(f) / SR
    return np.sin(ph) * e


def fwump(rng, dur=0.3):
    n = int(dur * SR)
    e, t = _env(n, 0.01, 12)
    sos = butter(2, 400, "lp", fs=SR, output="sos")
    return sosfilt(sos, rng.standard_normal(n)) * e * 2.5


def thud(dur=0.15):
    n = int(dur * SR)
    e, t = _env(n, 0.002, 30)
    return np.sin(2 * math.pi * 90 * t) * e


def add(buf, clip, at, gain, pan=0.0):
    if at >= len(buf):
        return
    end = min(len(buf), at + len(clip))
    c = clip[: end - at] * gain
    buf[at:end, 0] += c * math.cos((pan + 1) * math.pi / 4)
    buf[at:end, 1] += c * math.sin((pan + 1) * math.pi / 4)


def build_audio(sim, out_wav, seed=2):
    rng = np.random.default_rng(seed)
    cfg = sim["cfg"]
    fr = sim["frames"]
    fps = cfg.fps
    n_frames = len(fr)
    total = n_frames / fps + 1.0
    N = int(total * SR)
    buf = np.zeros((N, 2))
    tt = np.arange(N) / SR

    heat = np.array([f["heat"] for f in fr])
    hot = np.clip((np.log10(np.maximum(heat, 1)) - 2) / 5.5, 0, 1)
    hot_s = np.interp(tt, np.arange(n_frames) / fps, hot)
    er = np.array([0.0 if f["erupt"] is None else min(1.0, f["erupt"] / 2.5) for f in fr])
    er_s = np.interp(tt, np.arange(n_frames) / fps, er)

    # wind bed (stereo, slow gusts), fades a bit as the lava takes over but never disappears
    for ch in range(2):
        sos = butter(2, [250, 1400], "bandpass", fs=SR, output="sos")
        wind = sosfilt(sos, rng.standard_normal(N))
        gust = 0.6 + 0.4 * np.sin(2 * math.pi * (0.07 + 0.02 * ch) * tt + ch)
        buf[:, ch] += 0.10 * wind * gust * (1 - 0.6 * hot_s)
    # lava rumble grows with heat, roars at the eruption
    sos = butter(2, 140, "lp", fs=SR, output="sos")
    rum = sosfilt(sos, rng.standard_normal(N)) * 4 + 0.6 * np.sin(2 * math.pi * 41 * tt)
    roar_sos = butter(2, [200, 2500], "bandpass", fs=SR, output="sos")
    roar = sosfilt(roar_sos, rng.standard_normal(N))
    for ch in range(2):
        buf[:, ch] += 0.05 * rum * (0.25 + 1.4 * hot_s) + 0.25 * roar * er_s ** 1.2

    hiss_c = [hiss(rng) for _ in range(4)]
    fw = [fwump(rng) for _ in range(3)]
    th = thud()
    for fi, f in enumerate(fr):
        at = int(fi / fps * SR)
        for x in f["cool"][:3]:
            add(buf, hiss_c[fi % 4], at, 0.22, (x - cfg.crater_x) / 300)
        if f["melt"]:
            add(buf, hiss_c[(fi + 1) % 4], at, 0.09 * min(3, f["melt"]), 0.0)
        ups = f["heatup"][:3]
        for k, x in enumerate(ups):
            # pitch climbs with the heat
            step = min(24, max(0, int(4 * math.log10(max(heat[fi], 1)))))
            add(buf, blub(110 * 2 ** (step / 12)), at + k * 300, 0.32 / max(1, len(ups) ** 0.5),
                (x - cfg.crater_x) / 300)
        if f["launch"]:
            add(buf, fw[fi % 3], at, 0.10 * min(3, f["launch"]) ** 0.5)
        if f["land"]:
            add(buf, th, at, 0.12 * min(4, f["land"]) ** 0.5, float(rng.uniform(-0.6, 0.6)))

    if sim["erupt_frame"] is not None:
        at = int(sim["erupt_frame"] / fps * SR)
        n = int(3.5 * SR)
        t = np.arange(n) / SR
        boom = np.sin(2 * math.pi * 38 * t * (1 - 0.25 * t / 3.5)) * np.exp(-1.2 * t)
        add(buf, boom, at, 0.9)
        add(buf, fwump(rng, 1.5) * 1.0, at, 0.6)

    end = int(n_frames / fps * SR)
    tail = int(0.5 * SR)
    buf[end - tail:end] *= np.linspace(1, 0, tail)[:, None]
    buf[end:] = 0
    buf[: int(0.3 * SR)] *= np.linspace(0, 1, int(0.3 * SR))[:, None]
    buf /= np.abs(buf).max() or 1
    wavfile.write(out_wav, SR, (buf * 0.89 * 32767).astype(np.int16))
