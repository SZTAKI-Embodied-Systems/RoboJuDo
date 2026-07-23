# Kimodo "reach bottle" motion — deploy on the real G1

This branch adds `assets/motions/g1/kimodo_reach_motions.pt`, a self-contained 2-clip
library generated from a Kimodo text-to-motion export (stand → arm reach to a ~0.9 m
bottle → hold, ~28 s, static base). It runs with the standard tracker pipeline —
nothing else in the repo is changed and `g1_bones_seed_selection.pt` is untouched.

| Index | Clip | Notes |
|---|---|---|
| 0 | `reach` | **bias-compensated reference — use this one** |
| 1 | `baseline` | raw Kimodo export, comparison only. The tracker takes the left arm ~15 cm too high and presses the shoulder into the torso — do not demo. |

Clip 0 was verified sim2sim against the same `unified_pipeline.onnx` used on hardware:
hold height 0.793–0.797 m vs 0.800 m target, no shoulder–torso collision, balance
stable, only light wrist–thigh brushes (≤3 mm) while the hands hang at start/end.

## Start (same as any other motion, see `deploy_commands.md`)

```bash
python scripts/run_tracker_pipeline.py -c g1_protomotions_tracker_real \
    --motion-path assets/motions/g1/kimodo_reach_motions.pt --motion-index 0
```

Controls unchanged: Up/Down = clip index, X = start motion, V = return to standing,
R1 + A = damping / emergency stop.

## Notes for the first hardware run

- **Let the robot balance and settle for several seconds before pressing X.** The
  tracker policy carries action history — starting from an unsettled state lands in a
  degraded mode where the arm hugs the body and the reach falls short. If the reach
  looks wrong: V, let it stand quietly a few seconds, X again.
- The **wide, toe-out stance is in the reference itself** (Kimodo export), not a
  malfunction — feet ~0.32 m apart, left foot turned out ~23°.
- If reaching over a real table: the reaching wrist clears 0.75 m at the top.
- First run: spotter recommended, table area clear.
