---
name: animation-quality-review
description: Review an animation render for stiffness, jitter, pops, broken mechanics and weak impacts using fights/qc.py numbers plus frame-by-frame sheets and a normal-speed clip. Use after every animation change and before delivering any video.
---

# Animation quality review

A render is not done because the code runs. It is done when this review
passes at normal speed AND frame by frame.

## 1. Automatic checks

```bash
python3 fights/qc.py --fight NAME            # improved
python3 fights/qc.py --fight NAME --classic  # original keys/mechanics, for A/B
```

| Metric | Means | Target (drawn fights) |
| --- | --- | --- |
| `knee_rev_frac`, `knee_flips` | knees bent backwards / flipping sides | 0, 0 |
| `elbow_hyper_frac` | elbows bent the wrong way > 15 deg | 0 |
| `facing_pops` | whole body mirrors in one frame | 0 |
| `bone_ratio_range` | limb length vs rest (turn frames excluded) | limbs 1.0-1.0, torso 0.84-1.13 |
| `lowest_joint` | below 0 = limb through the ground | >= -6 |
| `pops` | joint jumps > 2.6x its neighbour frames | only inside smeared swings; check each one in a sheet |
| `hip_jerk` | hip acceleration spikes outside impacts | look at each; OK on launches/landings |
| `foot_slide_frames` | a grounded foot skating | only on deliberate slides/skids |
| `grip_err_*` | back hand off the shaft | small (< 13 units, while out of reach) |
| `dead_holds` | >= 10 frames of total stillness | 0 (moving holds) |
| `air_bumps` | jump arc reversing mid-air | 0, or explained (hits mid-air) |

Compare against the previous run. A change must not make any metric worse
without a reason you can name.

## 2. Frame by frame

```bash
python3 fights/preview.py --fight NAME --t0 A --t1 B --every 2 --out s.png
python3 fights/preview.py --fight NAME --frames 120,121,122 --scale 1 --cell 700 --crop 0.38,0.68 --out d.png
```
Read each sheet and check, for every exchange:
- [ ] anticipation visible before every attack (2+ frames moving the other way)
- [ ] contact frame: weapon touches the target/blade, nothing passes through a body
- [ ] hit reaction moves the whole body, recoil direction matches the blow
- [ ] arcs: hands and blades curve; no straight-line hand paths (`--onion`)
- [ ] silhouettes readable; no limb hidden in the torso
- [ ] no disappearing limbs, weapon always in the hand, proportions stable
- [ ] effects (ghosts, smears, trails, flashes) don't hide the pose
- [ ] feet don't skate; landings squash, launches stretch
- [ ] turns go through in-betweens

## 3. Normal speed

```bash
python3 fights/preview.py --fight NAME --t0 A --t1 B --clip clip.mp4
```
Watch for: rhythm (fast vs slow contrast), moves that feel floaty (too even
spacing) or robotic (everything arriving at once), hit-stops that feel too
long, camera shake that hides the contact. You can't watch video here: step
through the clip with `ffmpeg -ss T -i clip.mp4 -frames:v 1` or sheets at
`--every 1` to judge spacing, and say plainly that judgement is from frames.

## 4. Report

List each remaining issue with its timestamp, what is wrong, and the fix you
made or propose. Re-render and re-review after fixing; never deliver the
first render. Performance: a full 25 s render should stay under ~15 min on 4
cores; if a change doubles it, find out why.
