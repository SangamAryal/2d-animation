# 2d-animation

Code-made short videos.

- `katana/`: satisfying ball physics sims (a spinning katana that splits every ball it cuts).
- `fights/`: 2D stick-figure katana fights (bone rig, keyframed choreography, slash trails, impact frames, code-made sound).
  Render: `python3 fights/render.py OUT.mp4 --fight power` (or `patience`; add `--wide` for 16:9, `--scale 0.5` for a quick preview).
  Sound effects are real CC0 recordings in `fights/sfx/` (sources in `fights/sfx/CREDITS.md`).
  Needs `pip install numpy scipy skia-python` and `apt-get install libegl1 libgl1`.

## Hand-drawn motion layer (fight 07 v2+)

Fights that set `drawn=True` get anatomical mechanics (knees forward, no hyperextended elbows, IK two-hand grip, flips around the body's centre, drawn turns), body knockback on hits, moving holds, curved drag-bent limbs and solid smears.

- Original vs improved: `python3 fights/render.py OUT.mp4 --fight scythe [--classic]`
- Motion QC numbers: `python3 fights/qc.py --fight scythe [--classic]`
- Review sheets / clips: `python3 fights/preview.py --fight scythe --t0 2.6 --t1 4 --out sheet.png` (or `--clip clip.mp4`)
- Claude Code skills in `.claude/skills/`: `/hand-drawn-animation-director`, `/stick-fight-animation`, `/2d-animation-principles`, `/animation-quality-review`.
