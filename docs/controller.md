# Controller

**Controller** is the component that gives `ctrl_data` to the robot.

## [Controller](#controller)

`Controller` is the base class for all controllers. It defines the interface that all controllers must implement.

---
We provide the following controllers:
- [JoystickCtrl](#controller--joystickctrl)
- [UnitreeCtrl](#controller--unitreectrl)
- [KeyboardCtrl](#controller--keyboardctrl)
- [MotionCtrl](#controller--motionctrl)
- [BeyondmimicCtrl](#controller--beyondmimicctrl)

## [Controller](#controller) > [JoystickCtrl](#controller--joystickctrl)

`JoystickCtrl` is the controller that controls the robot using the joystick. It is a subclass of `Controller` and implements the interface defined in `Controller`.

script:
  - [joystick_ctrl.py](../robojudo/controller/joystick_ctrl.py)

Example data of Xbox Joystick with Linear Triggers:

`ctrl_data`:`dict`, the control data.
  - `axes`: `dict[str, float]`:
    - `LeftX`: left axes x value. Range: [-1, 1]
    - `LeftY`: left axes y value. Range: [-1, 1]
    - `RightX`: Right axes x value. Range: [-1, 1]
    - `RightY`: Right axes y value. Range: [-1, 1]
    - `LT`: left trigger value. Range: [0, 1]
    - `RT`: right trigger value. Range: [0, 1]
  - `button_event`: `list[dict]`:
    `dict`:
      - `name`: the name of the button. like `A`, `B`, `X`, `Y`...
      - `press`: whether the button is pressed. `bool`. `True` for `press`, `False` for `release`
      - `timestamp`: the time when the button event occurs. `float`
      - `type`: the type of the button event.

`command`: `list` of commands when `triggers` or `triggers_extra` are detected.

**example**:
```json
{'axes': {'LeftX': 0.0, 'LeftY': 0.0, 'RightX': 0.0, 'RightY': 0.0, 'LT': 0.0, 'RT': 0.0}, 'button_event': [{'type': 'button', 'name': 'A', 'pressed': False, 'timestamp': 1758886189.6776087}]}
```

You can set Hotkeys in JoystickCtrlCfg:
```python
JoystickCtrlCfg(
    triggers_extra={
        "RB+Down": "[POLICY_SWITCH],0",
        "LB+RB+A": "COMBO_TEST",
    }
),
```
when you press the `RB+Down` button, the command will be `["[POLICY_SWITCH],0"]`.

💡We have joystick mapping config for different platforms and Joystick types. 

> For KEY name and more details, please refer to the [joystick.py](../robojudo/controller/utils/joystick.py)

## [Controller](#controller) > [UnitreeCtrl](#controller--unitreectrl)

`UnitreeCtrl` is the controller that controls the robot using the `UnitreeG1` controller. It is a subclass of `Controller` and implements the interface defined in `Controller`. 

> ⚠️ If you don't connect to a Unitree robot, `UnitreeCtrl` won't work.

script:
- [unitree_ctrl.py](../robojudo/controller/unitree_ctrl.py)

`ctrl_data` and `command` are the same as `JoystickCtrl`.

## [Controller](#controller) > [KeyboardCtrl](#controller--keyboardctrl)

`KeyboardCtrl` is the controller that controls the robot using the keyboard. It is a subclass of `Controller` and implements the interface defined in `Controller`.

script:
  - [keyboard_ctrl.py](../robojudo/controller/keyboard_ctrl.py)
  
`ctrl_data`:`list[dict]`, the control data.
  `dict`:
   - `type`: the type of the input. `str`. `keyboard`
   - `name`: the name of the input key. `str`. like `a`, `Key.ctrl_l`, `Key.space`, `\x06`...
   - `pressed`: the value of the input. `bool`. `True` for `press`, `False` for `release`.
   - `timestamp`: the time when the input event occurs. `float`

`command`: `list`, only generate when you set `triggers`, otherwise, the command will be `[]`.

**example**:
```
[{'type': 'keyboard', 'name': 's', 'pressed': True, 'timestamp': 1758888074.643119}]
```

Similarly, you can set command triggers:
```python
KeyboardCtrl(
  cfg_ctrl=KeyboardCtrlCfg(
      triggers_extra={
          "Key.space": "[TEST]",
          "\x01": "[CTRL_A]",
      }
    )
  )
```
when you press the `Ctrl+A` button, the command will be `[CTRL_A]`.

💡For more details, please refer to the [keyboard.py](../robojudo/controller/utils/keyboard.py)


## [Controller](#controller) > [MotionCtrl](#controller--motionctrl)

`MotionCtrl` is the controller that controls the robot using the motion. It is a subclass of `Controller` and implements the interface defined in `Controller`.

`MotionCtrl` usually is used on mimic task to provide refer motion.

`ctrl_data`:`dict`, the control data.
  - `_motion_track_bodies_extend_id`: `int`: the id of the extended body.
  - `_robot_track_bodies_extend_id`: `int`: the id of the extended body.
  - `rg_pos_t`: `np.ndarray`: link position.
  - `body_vel_t`: `np.ndarray`: link velocity.
  - `root_pos`: `np.ndarray`: root position.
  - `root_vel`: `np.ndarray`: root velocity.
  - `root_rot`: `np.ndarray`: root rotation. w-last quat.
  - `root_ang_vel`: `np.ndarray`: root angular velocity.
  - `hand_pose`(Optional): `np.ndarray`: hand pose.

`MotionCtrl` can be set by `MotionCtrlCfg`. For instance, `G1MotionCtrlCfg`:

```python
G1MotionCtrlCfg(
    motion_name="amass_all",
)
```

Your motion file should be placed in the `assets/resources/motions/{robot}/phc` directory.

## [Controller](#controller) > [BeyondMimicCtrl](#controller--beyondmimicctrl)

`BeyondMimicCtrl` is the controller for `BeyondMimicPolicy`. It is a subclass of `Controller` and implements the interface defined in `Controller`.

You don't need to master `BeyondMimicCtrl`. It is just designed for `BeyondMimicPolicy`. You can set it with config:

```python
G1BeyondmimicCtrlCfg(
  motion_name="dance1_subject2", # only when policy: use_motion_from_model=False
)
```

## [Controller](#controller) > [ApiCtrl](#controller--apictrl)

`ApiCtrl` is the controller that receives COMMANDS from API requests.
It runs an in-process FastAPI server in a daemon thread so commands can be sent
programmatically from any HTTP client.

script:
  - [api_ctrl.py](../robojudo/controller/api_ctrl.py)

### Request schema

```
POST <path>          (default: /command)
Content-Type: application/json

{"command": "<COMMAND_NAME>", "passkey": "<PASSKEY>"}
{"command": "<COMMAND_NAME>", "arg": <integer>, "passkey": "<PASSKEY>"}
```

The `arg` field is **required** for commands listed in `command_args` (e.g.
`[MOTION_SET]`) and **forbidden** for all other commands.
The `passkey` field is **required** for every request and must match
`ApiCtrlCfg.passkey`.

### Response

```json
{"status": "ok", "command": "[MOTION_SET],18"}
```

HTTP `401` is returned when passkey is missing or invalid.
HTTP `422` is returned when the command is not in `allowed_commands`, the `arg`
is required but missing, or the `arg` is disallowed. HTTP `503` is returned
when the queue is full.

### Config

`command`: `list` of COMMANDS emitted when valid POST requests arrive.  The
string format is identical to what `KeyboardCtrl` and `JoystickCtrl` produce,
for example `[SHUTDOWN]` or `[MOTION_SET],18`.

`command_args`: maps a command name to either `None` (all args accepted) or a
list of allowed integer values. If a command appears in `command_args`, the
`arg` field is **required** and must match (or be allowed if `None`).
Commands not listed in `command_args` must be sent without an `arg` field.

**Example `ApiCtrlCfg`:**
```python
ApiCtrlCfg(
    host="0.0.0.0",
    port=8000,
    path="/command",
  passkey="CHANGE_ME",
    allowed_commands=[
        "[SHUTDOWN]",
        "[MOTION_RESET]",
        "[MOTION_FADE_IN]",
        "[MOTION_FADE_OUT]",
        "[MOTION_SET]",
    ],
    command_args={
        "[MOTION_SET]": None,  # None = all args accepted (default)
        # "[MOTION_SET]": list(range(10)),  # Restrict to clips 0–9
    },
)
```

**Example POST requests:**
```bash
# No argument — fires [SHUTDOWN]
curl -sX POST http://localhost:8000/command \
     -H 'Content-Type: application/json' \
  -d '{"command": "[SHUTDOWN]", "passkey": "CHANGE_ME"}'

# Integer argument — fires [MOTION_SET],18
curl -sX POST http://localhost:8000/command \
     -H 'Content-Type: application/json' \
  -d '{"command": "[MOTION_SET]", "arg": 18, "passkey": "CHANGE_ME"}'
```

See `g1_protomotions_tracker` in
[g1_cfg.py](../robojudo/config/g1/g1_cfg.py) for a full pipeline example that
combines `KeyboardCtrl` and `ApiCtrl`.
```