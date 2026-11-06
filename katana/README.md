# Ball sims (Katana and friends)

Satisfying ball physics shorts, all in one look: a glowing ring, a live ball counter, one colour per split generation.

Scenarios (`scenarios.py`):
- `katana`: a katana spins in the middle; every ball it cuts splits in two.
- `shuriken`: a throwing star bounces around the ring, slicing as it goes (×2).
- `laser`: a beam sweeps through the ring; every ball it hits splits into three.
- `blackhole`: every hard wall hit doubles a ball, while a growing black hole in the middle swallows them.

Everything is made in code: the physics (`sim.py`), the picture (`render.py`, Skia) and the
sound (`audio.py`, synthesized with numpy, no samples).

## Run

```bash
sudo apt-get install -y ffmpeg libegl1 libgl1   # libegl1 is needed by skia-python on Linux
pip install -r requirements.txt
python3 make_sample.py out/laser.mp4 --scenario laser --stills out/stills
```

Output is 1080x1920 (Shorts), 60 fps, audio normalised to -14 LUFS. A ~25 s video renders in about 45 s on 4 cores.

## Knobs

- A new scenario is a new entry in `scenarios.py`: title, subtitle, cutter style, palette, ring colour, and a `SimConfig`.
- `SimConfig` in `sim.py`: ring and ball size, gravity, blades (any number, any length), spin speed, moving cutter, pieces per cut, cut cooldown (sets how fast the count grows), wall splitting, black hole, ball cap.
- `--seed` gives a different run with the same look.

Fonts: Inter Display (SIL Open Font License), bundled in `fonts/`.
