# Kimodo "reach bottle" motion — deploy on the real G1

This branch adds two self-contained motion libraries generated from a Kimodo
text-to-motion export (stand → arm reach to a ~0.9 m bottle → hold, static base).
They run with the standard tracker pipeline — nothing else in the repo is changed
and `g1_bones_seed_selection.pt` is untouched.

**Use `kimodo_reach_v2.pt`.** The first hardware test of the v1 clip looked "messy":
28 s with ~15 s of near-static time, during which the tracker's micro-adjustments
(feet shuffling, slow creep) dominate what you see. v2 is the same poses retimed to
17.3 s — dead time compressed, reach brisk — matching the pace of the stock demo
clips (box/salsa), which is what makes those look crisp.

### `kimodo_reach_v2.pt` (recommended)

| Index | Clip | Notes |
|---|---|---|
| 0 | `reach_v2` | **retimed + bias-compensated — demo this** (17.3 s) |
| 1 | `reach_v1` | original-timing compensated clip, comparison (27.8 s) |

### `kimodo_reach_motions.pt` (v1, kept for reference)

| Index | Clip | Notes |
|---|---|---|
| 0 | `reach` | bias-compensated, original slow timing |
| 1 | `baseline` | raw Kimodo export — do not demo (arm ~15 cm high, shoulder presses torso) |

v2 clip 0 verified sim2sim against the same `unified_pipeline.onnx` used on hardware:
grasp-hold wrist within 4 cm of target (z +1.4 cm), no self-collision beyond a 4 mm
momentary wrist–thigh graze (equal to the stock seed clips), balance stable,
high-frequency wrist jitter below the stock point-hold clip.

## Start (same as any other motion, see `deploy_commands.md`)

```bash
python scripts/run_tracker_pipeline.py -c g1_protomotions_tracker_real \
    --motion-path assets/motions/g1/kimodo_reach_v2.pt --motion-index 0
```

**Start from a settled stand with a single X press.** `[MOTION_FADE_IN]` and
`[MOTION_RESET]` are the same handler — each (re)starts the clip at frame 0
immediately. Do NOT "fade in, wait, then reset": with v2's short intro the second
command lands mid-reach and snaps the arm down through the thigh. Let the robot
balance quietly for several seconds, then press X once. To replay, wait for the
clip to finish (robot returns to stand), then press X again.

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
