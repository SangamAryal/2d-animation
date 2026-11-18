---
name: 2d-animation-principles
description: Traditional 2D animation principles translated into concrete numbers and code moves for this repo's keyframe rig. Use when choosing poses, timing, easing, spacing, overlap or squash/stretch for any animated character.
---

# 2D animation principles, as code

60 fps output. 1 frame = 0.0167 s. "On ones" = a new drawing every frame.
Anime fights mix: holds and anticipations read like 2s/3s, strikes on ones.
We stay on ones (smooth) and get the anime rhythm from **spacing and holds**.

## Timing table (seconds of story time)

| Beat | Duration | Ease into it |
| --- | --- | --- |
| anticipation / wind-up | 0.10-0.25 (big moves 0.3+) | `back` |
| strike to contact | 0.06-0.12 | `snap` |
| hit-stop at contact | 0.05 light, 0.08-0.12 big, 0.14-0.16 kill | `stop(t, d)` |
| follow-through | 0.10-0.20 | `out` |
| settle to guard | 0.15-0.30 | `io` / `out` |
| turn around | 0.10 (automatic in drawn fights) | `Track.face` |
| readable hold | >= 0.25 before a big action | moving hold |

Rule of contrast: a fast move only reads fast next to a slower one. Never
key three moves in a row at the same speed.

## Principles -> what to do here

1. **Squash & stretch**: pose key `sq` (-0.16..0.13, clamped). Squash on
   crouch/landing/impact (`sq=-0.12..-0.16`), stretch on launch and full
   extension (`sq=0.08..0.13`). The torso stroke thins when stretched
   (volume). Root springs add landing squash automatically.
2. **Anticipation**: the wind-up goes the *opposite* way of the action
   (a forward cut winds back, a jump crouches). Key it with ease `back`.
3. **Staging**: the attacker's weapon and the target must both be visible at
   contact; keep fighters 120-260 units apart in exchanges.
4. **Straight ahead vs pose to pose**: we are pose to pose. Key extremes and
   breakdowns; the springs make the in-betweens.
5. **Follow-through & overlap**: springs in `motion.SPRINGS`: torso fast,
   head slower (lags), free arm loose (low frequency, low damping), weapon
   overshoots (`sw` damping ~0.55). Do not key every joint to arrive at once.
6. **Slow in / slow out**: `io` for moves between holds; `snap` only into
   contacts; `lin` only inside continuous spins/runs.
7. **Arcs**: angles, not positions. A hand path that is a straight line is a
   bug. Check with `preview.py --onion`.
8. **Secondary action**: headband tails, hood, tassel, breathing. They must
   never upstage the primary action.
9. **Timing**: see table. Spacing (how far a joint travels per frame) matters
   more than the number of frames.
10. **Exaggeration**: push extremes 15-30% past "realistic": deeper crouch,
    longer lunge, bigger twist; keep the in-betweens believable.
11. **Solid drawing**: proportions are fixed bones; only `sq` may change the
    torso. Knees bend forward, elbows never hyperextend (`solve_drawn`).
12. **Appeal**: clear silhouettes, asymmetry between left and right limbs,
    lines of action through the whole body (head-spine-leg as one curve).

## Breakdown poses

Between two keys whose limbs swap sides (e.g. wind-up behind -> cut in
front), add a breakdown key where the weapon passes overhead or low, so the
arc doesn't cut through the body. Put the breakdown ~40% of the way, with
the body already rotating toward the target (hips lead).

## Hand-drawn feel (drawn=True)

- Limbs drag-bend on fast swings (`render.drag_bows`) and joints are rounded
  (`draw.limb`): organic variation driven by motion, not random noise.
- No line boil or random jitter: Sangam wants smooth, not flicker.
- Smears: one solid swept shape per fast limb/weapon, only on frames where the
  joint jumps more than ~14 units.
