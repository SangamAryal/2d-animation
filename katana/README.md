# Katana ball sims

A katana spins inside a ring. Every ball it cuts splits in two and takes the next colour.
The count keeps doubling until the ring is full.

Everything is made in code: the physics (`sim.py`), the picture (`render.py`, Skia) and the
sound (`audio.py`, synthesized with numpy, no samples).

## Run

```bash
sudo apt-get install -y ffmpeg libegl1 libgl1   # libegl1 is needed by skia-python on Linux
pip install -r requirements.txt
python3 make_sample.py out/katana.mp4 --seed 7 --stills out/stills
```

Output is 1080x1920 (Shorts), 60 fps, audio normalised to -14 LUFS. A ~25 s video renders in about 45 s on 4 cores.

## Knobs

- `SimConfig` in `sim.py`: ring size, ball size, gravity, spin speed, cut cooldown (controls how fast the count doubles), ball cap.
- `PALETTE` in `render.py`: one colour per generation.
- `--seed` changes the run while keeping the look; `--title` changes the top text.

Fonts: Inter Display (SIL Open Font License), bundled in `fonts/`.
