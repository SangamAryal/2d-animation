---
name: stick-fight-animation
description: Choreograph and key a stick-figure weapon fight (sword, katana, scythe, spear, shield) in fights/choreo_*.py with readable attacks, blocks, dodges, hits and kills. Use when creating a new fight or rekeying an exchange.
---

# Stick-fight animation (this repo)

## Setup of a new fight

1. Copy the structure of `fights/choreo_scythe.py`: styles, `pose()` defs,
   `build(drawn=True)` returning `dict(fighters, events, end, title, hp,
   springy=True, fluid=True, drawn=drawn)`.
2. Register it in `render.FIGHTS`.
3. Fighter A starts left facing +1, B right facing -1. x in world units,
   a fighter is ~160 tall, exchanges happen 120-260 units apart.

## Angle conventions (rig.py)

Absolute angles in the fighter's frame: 0 up, 90 forward, 180 down, 270/-90
back. Keys: `T` torso, `H` head, `uaf/faf` front arm (holds weapon),
`uab/fab` back arm, `thf/shf` front leg, `thb/shb` back leg, `sw` weapon.
Scalars: `grip` (back hand on the weapon 0..1), `air`, `dy`, `rot` (whole-body
spin, accumulate it: `RA[0] += 360`), `sq`.

## The 4-beat attack (every attack, no exceptions)

```python
BK(t - 0.16, "r_high_wind", x + 6, "back")   # anticipation: opposite direction
BK(t - 0.04, "r_high_wind", x + 4, "lin", T=-20)  # coil: torso keeps winding
BK(t, "r_reap", x - 60, "snap")               # contact on the frame of the event
E(t, "clash" | "hit", ...); stop(t, 0.08)    # contact + hit-stop
BK(t + 0.20, "r_reap", x - 62, "out")         # follow-through, slight drift
BK(t + 0.45, "r_guard", x - 50, "out")       # recovery
```
- The body moves into the strike (x changes 20-60 units on the snap), hips
  lead: torso `T` leans into the cut before the arm finishes.
- The defender reacts on the *same* timestamp: block key `snap` at t, then a
  recoil key 0.02-0.1 later that moves them back 10-40 units.

## Reactions

| Situation | Keys and events |
| --- | --- |
| blocked | defender `block_*` snap at t, `T` pushed back -8..-12 at t+0.04; `clash` big for heavy blows |
| hit | `hit` event with `by/on/dmg/part`; victim pose `recoil`/`r_hurt` snap at t+0.01, `stagger` out at t+0.25, moved 30-150 back; drawn fights add root knockback automatically |
| knockdown | `tumble` with `air` and `rot`, `fallen` with `in` ease, `thud` + `skid` |
| dodge | crouch (`sq=-0.15`) on the attacker's anticipation, not on the contact |
| jump / flip | crouch -> `jump_tuck` (air 70-95, rot 180) -> land pose (rot 360), accumulate rot |
| kill | `slowmo` before, `decap` / `dmg amt=100`, `kill`, stop 0.16, body `kneel` -> `fallen` |

## Contacts and weapons

- **Sangam's #1 complaint: sparks with blades not touching.** In drawn fights
  `fights/contact.py` runs on every `clash`, `hit` and `decap`: it re-times
  the event (and its hit-stop/kill cues) to the closest moment and adds a
  small eased correction (weapon angle / hip x) so the shapes truly touch,
  and puts sparks/blood at the real contact point. Still key contacts close
  by eye: check `Fight(...).contact_report` and `f.corr[...]`; a correction
  above ~40 deg or ~50 units means the keys are wrong (e.g. a swing that
  passes behind the attacker) and must be rekeyed.
- Decapitations: the neck must sit inside the cutting part of the blade.
- Kicks: `part="ftf"`; key the kick so the foot reaches the torso (step in),
  chamber with `kick_wind` first. Blunt hits (feet, hands, butt) don't bleed.

- Weapons attach to the front hand by construction; the back hand takes the
  grip with IK (`grip=1`), smoothed over ~5 frames. Don't key grip on/off on
  the contact frame.
- Weapons must not pass through bodies at contact: check the frame of every
  `hit`/`clash` in a sheet. If a thrust/butt strike lands, the victim must be
  pushed out of the weapon's line within 0.1 s and the attacker must retract.
- Choreography reads left-right: alternate who attacks, 2-4 beats per
  exchange, a reset/standoff (moving hold, >= 0.4 s) before a climax.

## Don'ts

- No mirror pops: change sides with `Track.face`, drawn fights turn in 0.1 s.
- No feet skating: big x changes while grounded need step events or a
  dash/run pose; `feet.Planter` plants and steps automatically.
- No hand-made ghosts or flashes to hide a weak pose: fix the pose.
- Insert rounds with `_shift()` so later keys and events move together.
