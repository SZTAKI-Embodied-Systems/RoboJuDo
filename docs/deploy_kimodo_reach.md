# Kimodo "reach bottle" motion — deploy on the real G1

This branch adds two self-contained motion libraries generated from a Kimodo
text-to-motion export (stand → arm reach to a ~0.9 m bottle → hold, static base).
They run with the standard tracker pipeline — nothing else in the repo is changed
and `g1_bones_seed_selection.pt` is untouched.

**Use `kimodo_reach_v10.pt`.** Built on the v2 retiming after sim review of v2-v4
and the first v5 hardware run:

- **table-safe approach**: the hand first rises beside the body to almost grasp
  height, then moves forward onto the bottle from slightly above — it never dips
  below ~0.82 m while forward of the table edge (v5 swept forward at ~0.75 m and
  hit the table). The return mirrors it: up and back off the bottle, then down;
- **3 s dwell at the grasp point** before the lift (time to close a gripper);
- start/end stand pose holds the hands ~11 cm further out than the raw export
  (v5's 8 cm still brushed the legs on hardware; 13 cm read too wide);
- the return descends OUTSIDE the leg: sideways-out at height to directly above
  the stand hand position, then straight down — no diagonal drop across the
  thigh. Ends holding the exact start pose. 16.3 s.

### `kimodo_reach_v10v9.pt` (recommended — A/B switchable)

| Index | Clip | Notes |
|---|---|---|
| 0 | `reach_v10` | **+10 cm raised grasp phase (hardware compensation) — demo this** |
| 1 | `reach_v9` | same motion without the 10 cm raise, for comparison |

Switch clips with gamepad Up/Down (then X to start), or `[MOTION_SET]` with
the index over the command API. Both clips are 16.3 s with identical timing.

### `kimodo_reach_v10.pt` (single clip, same as index 0 above)

| Index | Clip | Notes |
|---|---|---|
| 0 | `reach_v10` | table-safe raised approach, grasp dwell, hands clear of legs (16.3 s) |

### `kimodo_reach_v5.pt` (superseded — approach sweeps at table height)

| Index | Clip | Notes |
|---|---|---|
| 0 | `reach_v5` | straight low approach, grasp dwell, 8 cm leg clearance (16.3 s) |

### `kimodo_reach_v2.pt` (superseded)

| Index | Clip | Notes |
|---|---|---|
| 0 | `reach_v2` | retimed + bias-compensated (17.3 s) — approach arcs up/down, no grasp dwell |
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
    --motion-path assets/motions/g1/kimodo_reach_v10.pt --motion-index 0
```

**Start from a settled stand with a single X press.** `[MOTION_FADE_IN]` and
`[MOTION_RESET]` are the same handler — each (re)starts the clip at frame 0
immediately. Do NOT "fade in, wait, then reset": with v2's short intro the second
command lands mid-reach and snaps the arm down through the thigh. Let the robot
balance quietly for several seconds, then press X once. To replay, wait for the
clip to finish (v5 returns to and holds the exact start stand), then press X again.

Controls unchanged: Up/Down = clip index, X = start motion, V = return to standing,
R1 + A = damping / emergency stop.

## Notes for the first hardware run

- **Let the robot balance and settle for several seconds before pressing X.** The
  tracker policy carries action history — starting from an unsettled state lands in a
  degraded mode where the arm hugs the body and the reach falls short. If the reach
  looks wrong: V, let it stand quietly a few seconds, X again.
- A **moderately wide stance is normal** — v5's reference legs are the G1 default
  stand (feet 0.24 m), but the tracker picks its own stance, ~0.25–0.28 m. (The
  original Kimodo export's 0.32 m toe-out terpesz is already edited out.)
- If reaching over a real table: the reaching wrist clears 0.75 m at the top.
- First run: spotter recommended, table area clear.
