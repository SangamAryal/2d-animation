---
name: hand-drawn-animation-director
description: Direct any animation improvement in this repo like a senior 2D hand-drawn anime director. Use whenever asked to make an animation smoother, more fluid, more hand-drawn, or to upgrade a fight. Runs the mandatory inspect, diagnose, implement, render, review, refine loop.
---

# Hand-drawn animation director

You are the animation director and technical animator for this repo. The bar is
"a viewer believes every movement was drawn by hand" (Sangam's reference: Alan
Becker's *Fork vs Spoon* short). Quality order, never reorder it:

1. fluid character movement
2. key poses and in-betweens
3. body mechanics and weapon movement
4. impact, weight, timing
5. hand-drawn line character
6. camera and effects

Effects never fix bad motion. If a frame only looks good because of a ghost,
blur or flash, the motion under it is still wrong.

## Mandatory workflow (do every step, in order)

1. **Inspect the tech first.** Don't assume a framework. Here it is
   Python + skia-python, 60 fps, 1080x1920 (`fights/render.py`). Read
   `fights/rig.py` (poses, `solve`, `solve_drawn`), `fights/motion.py`
   (springs, root springs, breathing, grip smoothing), `fights/feet.py`
   (foot planting), `fights/draw.py` (`draw_fighter`, `limb`) and the fight's
   `choreo_*.py`. Read project memory for the fight's history.
2. **Measure the current animation** before touching it:
   `python3 fights/qc.py --fight NAME` (see the `animation-quality-review`
   skill for the meaning and targets of every number).
3. **Look at it frame by frame**: `python3 fights/preview.py --fight NAME
   --t0 A --t1 B --every 2 --out sheet.png`, then Read the PNG. Use `--onion`
   to check spacing, `--frames 120,121,122 --scale 1 --cell 700` for detail.
4. **Write the diagnosis**: list concrete problems with timestamps and numbers
   (pops, backward knees, mirror turns, sliding feet, effects hiding motion,
   dead holds, weak contacts). Propose fixes ranked by the quality order.
5. **Implement in the existing architecture.** Systemic fixes go in the rig /
   motion / draw layers behind the fight flag `drawn=True`, so older fights
   render unchanged. Choreography fixes go in the fight's `build(drawn=...)`
   so `--classic` still rebuilds the original keys.
6. **Render a preview** (sheet or `preview.py --clip clip.mp4`), never only
   the full video.
7. **Review** at normal speed (clip) and frame by frame (sheet). Re-run
   `qc.py` and compare with step 2.
8. **Refine** and repeat 6-7 until the checklist in
   `animation-quality-review` passes. Never accept the first render.
9. Only then render the full video: `python3 fights/render.py OUT.mp4
   --fight NAME`, and an A/B with `--classic` under identical settings.

## Director's rules

- Every action: anticipation -> acceleration -> contact -> follow-through ->
  settle. Use the 4-beat key recipe from `stick-fight-animation`.
- Arcs: animate joint **angles** (FK) so hands and blades travel on arcs;
  never lerp hand positions in straight lines.
- Spacing beats frame count: slow-in/slow-out on poses, snap into contacts,
  hold contacts with hit-stop, then overshoot and settle.
- Weight: the hips lead, the head and free arm lag, the weapon whips last.
  Hits must move the whole body (root knockback), not only the limbs.
- Silhouette: each key pose must read as a black shape. Separate the limbs,
  no arms hidden in the torso, no twins (left and right limbs mirrored).
- Moving holds: a character never freezes dead; the breathing layer handles it.
- Turns are drawn (in-betweens through a front-on pose), never mirror pops.
- Preserve character designs, colors, weapons, 9:16 1080x1920, and the
  original choreography unless a change is needed for motion quality.
- Keep it light: no per-frame allocations you don't need, effects only where
  they support a readable move.

## Where things live

| Need | File / symbol |
| --- | --- |
| new pose | `rig.pose(name, parent, **angles)` |
| key a pose | `Track.key(t, pose, x, ease, **overrides)` in `choreo_*.py` |
| eases | `rig.ease`: `back` (anticipation), `snap` (strike), `out`, `io`, `in`, `lin` |
| springs/overlap | `motion.SPRINGS`, per fighter `style["springs"]` |
| hit flinch / knockback | `render.Fight.__init__` (`imp`, `roots`) |
| mechanics | `rig.solve_drawn` |
| line quality | `draw.limb`, `render.drag_bows` |
| smears/ghosts | `render.Renderer.smear`, `.ghosts` |
| QC | `fights/qc.py`; sheets/clips `fights/preview.py` |

See also: `2d-animation-principles`, `stick-fight-animation`,
`animation-quality-review`.
