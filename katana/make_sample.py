"""Render one Katana video: sim -> audio -> picture -> mp4.

Usage: python3 make_sample.py OUT.mp4 [--seed N] [--title TEXT] [--stills DIR]
"""
import argparse
import os
import subprocess
import tempfile

from audio import build_audio
from render import render_still, render_video
from sim import SimConfig, simulate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--title", default="KATANA")
    ap.add_argument("--stills", default=None, help="folder for review stills")
    a = ap.parse_args()

    sim = simulate(SimConfig(seed=a.seed))
    n = len(sim["pos"])
    print(f"sim: {n} frames ({n / sim['cfg'].fps:.1f}s), ring full at frame {sim['full_frame']}")
    with tempfile.TemporaryDirectory() as td:
        raw = os.path.join(td, "raw.wav")
        wav = os.path.join(td, "mix.wav")
        build_audio(sim, raw)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                        "-ar", "48000", wav], check=True)
        render_video(sim, a.out, wav, a.title)
    if a.stills:
        os.makedirs(a.stills, exist_ok=True)
        for fi in [int(n * 0.1), int(n * 0.5), int(n * 0.75), n - 40]:
            render_still(sim, fi, os.path.join(a.stills, f"frame{fi:05d}.png"), a.title)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
