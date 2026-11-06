# 2d-animation

Code-made short videos.

- `katana/`: satisfying ball physics sims (a spinning katana that splits every ball it cuts).
- `fights/`: 2D stick-figure katana fights (bone rig, keyframed choreography, slash trails, impact frames, code-made sound).
  Render: `python3 fights/render.py OUT.mp4 --fight power` (or `patience`; add `--wide` for 16:9, `--scale 0.5` for a quick preview).
  Sound effects are real CC0 recordings in `fights/sfx/` (sources in `fights/sfx/CREDITS.md`).
  Needs `pip install numpy scipy skia-python` and `apt-get install libegl1 libgl1`.
