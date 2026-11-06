"""Render volcano vs snowstorm: python3 make_volcano.py OUT.mp4 [--seed N]"""
import argparse
import dataclasses
import os
import subprocess
import tempfile

from volcano_audio import build_audio
from volcano_render import render_video
from volcano_sim import VolcanoConfig, simulate


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()
    cfg = VolcanoConfig() if a.seed is None else dataclasses.replace(VolcanoConfig(), seed=a.seed)
    sim = simulate(cfg)
    print(f"{len(sim['frames']) / cfg.fps:.1f}s, eruption at frame {sim['erupt_frame']}")
    with tempfile.TemporaryDirectory() as td:
        raw, wav = os.path.join(td, "raw.wav"), os.path.join(td, "mix.wav")
        build_audio(sim, raw)
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", raw, "-af", "loudnorm=I=-14:TP=-1.5:LRA=11",
                        "-ar", "48000", wav], check=True)
        render_video(sim, a.out, wav)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
