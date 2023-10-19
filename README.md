# Stepper Motor Driver 🤖

This module allows for the control of a multiple stepper motors. It includes functionality for customization of stepping sequence, direction, duration, and speed of motor.

Python dependencies: **RPi.GPIO**, **threading**

## 🔧 Stepper Setup

In order to use the stepper module, there are a few stages to set up the appropriate motors:

- First, the GPIO mode must first be set. This can be done with `board_setup()`, either passing a string "BOARD" or "BCM".
- Next, `Motor` objects must be defined. This can be done with the `Motor()` constructor, which takes 4 pin integers as input. These pins should be in order as they appear on the stepper motor as A, B, C, and D.

## ▶️ Running Motors

To run one or more stepper motors, you can either use the `step_motor()` or `step_motors()` function. These both take similar inputs, except `step_motors()` takes _lists_ of arguments instead of one of each.

The arguments of `step_motor()` look like this:

```python
def step_motor(
    motor: Motor,
    num_steps: int,
    direction: int,
    sequence: Sequence = Sequences.WHOLESTEP,
    delay: float = MINIMUM_STEP_DELAY,
) -> None:
```

Here, you will specify your `Motor` object, as well as the number of steps, direction to spin, type of sequence, and step delay.

The number of steps is the number of stages you want your stepper to advance. This value can also be negative to reverse the direction.

Directions can be found within the `Directions` class, with `Directions.CLOCKWISE` and `Directions.COUNTER_CLOCKWISE`. You can also just enter 1 or -1, corresponding to the same directions, respectively.

Sequences can similarly be found within the `Sequences` class. There are four current sequences in this class:

- `Sequences.HALFSTEP` - Provides a higher torque but slower overall motor speed.
- `Sequences.WHOLESTEP` - Provides a lower torque but higher overall motor speed.
- `Sequences.LOCK` - "Locks" the specified motor so that turning is disabled magnetically.
- `Sequences.UNLOCK` - "Unlocks" the specified motor, setting all the pins to LOW.

The arguments of `step_motors()` look like this:

```python
def step_motors(
    motors: list[Motor],
    num_steps: list[int],
    directions: list[int],
    sequence: Sequence = Sequences.WHOLESTEP,
    delay: float = MINIMUM_STEP_DELAY,
    flag: bool = False,
) -> None:
```

The arguments remain the same, but the lists of motors, directions, and steps must all be of equal size. There is an additional argument to flag the start and end of all motor threads.

## 🎛️ Customizations

Custom sequences can be made with the `Sequence()` constructor. Its arguments look like this:

```python
def __init__(
        self,
        stages: list[tuple[int, int, int, int]],
        step_size: int = 1,
    ) -> None:
```

Sequences must be a list of four-pin "stage" tuples. Every stage has four integers that correspond to the level of each motor pin. Any non-zero integer will be interpreted as HIGH, and zero as LOW. An additional `step_size` integer indicates how many stages make up a single "step". For example, a halfstep sequence would have this value set to two, while a wholestep sequence would have this set to one.

## ❌ Troubleshooting

This module has many dependencies and flaws. `RPi.GPIO` is a very difficult module to work with, and is often the cause of many problems. If you would like assistance, feel free to send me an email.
