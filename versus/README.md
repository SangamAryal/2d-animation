# Versus sims (rule-based tug of war)

Two forces, rules written on screen, one big % meter. The meter dips low first, then one side snowballs into an absurd finish.

- `volcano_*`: volcano vs snowstorm. Every snowflake that lands in the crater cools the lava 10%; every lava bomb that falls back in heats it 50% and launches 2 more. Above 400% the snow melts into steam before it lands.

```bash
python3 make_volcano.py out/volcano.mp4 [--seed N]
```

Uses the same setup and fonts as `../katana` (numpy, scipy, skia-python, ffmpeg). The seed and rule numbers in `VolcanoConfig` were tuned so heat dips to ~16% around 20 s and erupts at ~41 s.
