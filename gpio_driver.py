#!/usr/bin/env python
"""
Allows for the control of a single stepper motor. step() function 
allows for customization of stepping sequence, direction, duration, and speed 
of motor. Includes a full and half-step sequence as well as single or offset 
stepping options.
"""
import time

import RPi.GPIO as GPIO

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "MIT"
__version__ = "1.2"
__maintainer__ = "Ben Kraft"
__email__ = "benjamin.kraft@tufts.edu"
__status__ = "Prototype"


MINIMUM_STEP_DELAY = 0.005

# Defines a "Direction" type
class Direction:
    """
    A class for motor directions. Tied to signed integers.
    """

    def __init__(self, value: int) -> None:
        self.value = value


# Defines motor spin directions
class Directions:
    """
    Establishes existing motor directions.
    """

    CLOCKWISE = Direction(1)
    COUNTER_CLOCKWISE = Direction(-1)


class Sequence:
    """
    A class for stepper motor sequences. Consist of 4-integer motor "stages".
    """

    def __init__(
        self, stages: tuple[tuple[int, int, int, int], ...], step_size: int = 1
    ) -> None:
        # Assigns members
        self.stages = stages
        self.step_size = step_size

    def lengthen(self, number: int):
        self.stages = self.stages * number


class Sequences:
    """
    # Establishes existing stepper motor sequences.
    """

    HALFSTEP = Sequence(
        stages=(
            (1, 0, 0, 0),
            (1, 1, 0, 0),
            (0, 1, 0, 0),
            (0, 1, 1, 0),
            (0, 0, 1, 0),
            (0, 0, 1, 1),
            (0, 0, 0, 1),
            (1, 0, 0, 1),
        ),
        step_size=2,
    )
    WHOLESTEP = Sequence(
        stages=(
            (1, 0, 0, 1),
            (1, 1, 0, 0),
            (0, 1, 1, 0),
            (0, 0, 1, 1),
        )
    )
    LOCK = Sequence(((1, 0, 0, 1),))
    UNLOCK = Sequence(((0, 0, 0, 0),))


class Motor:
    """
    A class for stepper motors. Consists of four pins.
    """

    def __init__(self, *pins: int) -> None:
        # Checks number of pins
        if len(pins) != 4:
            raise ValueError("Motor must consist of four integer pins.")
        # Sets all motor pins to output and disengages them
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)  # type: ignore
            GPIO.output(pin, False)  # type: ignore
        # Creates member
        self.pins = pins


BOARD_MODE = 10
BCM_MODE = 11


def main() -> None:
    """
    Runs main test motor protocol
    """
    start_time = time.time()

    try:
        board_setup("BCM")

    except KeyboardInterrupt:
        # Turns off pins left on
        board_cleanup()
    # Turns off pins left on
    board_cleanup()
    # Calculates and reports execution time
    elapsed_time = round((time.time() - start_time), 3)
    print("Execution time:", elapsed_time, "seconds")


def step(
    motors: tuple[Motor, ...],
    directions: tuple[Direction, ...],
    num_steps: int = 1,
    sequence: Sequence = Sequences.WHOLESTEP,
    delay: float = MINIMUM_STEP_DELAY * 2,
) -> None:
    """
    Allows for a specified number of steps to be run in a direction using a
    sequence of custom delay.
    """
    # Fits sequence to number of steps
    extended_sequence = extend_sequence(sequence, num_steps)
    # Creates list of sequences in correct orientations
    sequences_list = tuple(
        direction_sequence(extended_sequence, direction) for direction in directions
    )
    # Runs sequence with appropriate delay
    if len(motors) == 1:
        _run_motor(motors[0], sequences_list[0], (delay / sequence.step_size))
    elif len(motors) >= 2:
        _run_motors(motors, sequences_list, (delay / sequence.step_size))


def _run_motor(
    motor: Motor, sequence: Sequence, delay: float = MINIMUM_STEP_DELAY
) -> None:
    """
    Controls a single motor to execute a sequence.
    """
    if delay < MINIMUM_STEP_DELAY:
        raise ValueError(
            f"Too small of delay. Must be equal to or larger than {MINIMUM_STEP_DELAY}s."
        )
    # For each stage in sequence
    for stage in sequence.stages:
        # For each pin level in stage
        for pin_index, level in enumerate(stage):
            # Sets motor pin to specified level
            GPIO.output(motor.pins[pin_index], level)  # type: ignore
        # Delays between stages
        time.sleep(delay)


def _run_motors(
    motors: tuple[Motor, ...],
    sequences: tuple[Sequence, ...],
    delay: float = MINIMUM_STEP_DELAY,
) -> None:
    """
    Controls multiple motors to execute corresponding sequences.
    """
    if len(motors) != len(sequences):
        raise ValueError("Number of motors must match number of sequences!")
    # Raises error for too small delay
    if delay < MINIMUM_STEP_DELAY:
        raise ValueError(
            f"Too small of delay. Must be equal to or larger than {MINIMUM_STEP_DELAY}s."
        )
    # Acquires first set of stages as sample
    sample_stages = sequences[0].stages
    # Checks that all sequences have equal lengths
    if any(len(sequence.stages) != len(sample_stages) for sequence in sequences):
        raise ValueError("Sequences do not have congruent sizes!")

    # For each stage in sample
    for stage_index in range(len(sample_stages)):
        # Acquires first stage as sample
        sample_stage = sample_stages[0]
        # For each pin in stage
        for pin_index in range(len(sample_stage)):
            # For each motor:
            for motor_index, motor in enumerate(motors):
                # Acquires current stages
                current_stages = sequences[motor_index].stages
                # Finds pin level of stage
                level = current_stages[stage_index][pin_index]
                # Sets motor pin to specified level
                GPIO.output(motor.pins[pin_index], level)  # type: ignore
        # Delays between stages
        time.sleep(delay)


def extend_sequence(sequence: Sequence, num_steps: int) -> Sequence:
    """
    Iterates sequence to fit number of steps.
    """
    stages, step_size = sequence.stages, sequence.step_size
    # Divides number of specified steps by number of steps in sequence
    multiplier, remainder = divmod(num_steps, (len(stages) // step_size))
    # Prints warning if needed
    # if remainder:
    #     print(
    #         f"WARNING: Number of steps ({num_steps}) not factor of sequence ({len(stages)}). Future steps might mis-align."
    #     )
    # Creates a short sequence from remaining steps
    remainder_stages = stages[: (remainder * step_size)]
    # Builds a long sequence from "quotient" number of sequences and remainder
    return Sequence(stages * multiplier + remainder_stages, step_size)


def direction_sequence(sequence: Sequence, direction: Direction) -> Sequence:
    """
    Creates a sequence in corresponding direction.
    """
    return Sequence(sequence.stages[:: direction.value])


def lock_motors(motors: tuple[Motor]) -> None:
    """
    Runs a constant signal on the motor. WARNING: Do not keep on.
    """
    # Runs first step of sequence to lock the motor
    _run_motors(motors, (Sequences.LOCK,) * len(motors))


def unlock_motor(motors: tuple[Motor]) -> None:
    """
    Turns off all motor pins.
    """
    # Turns off all pins to motors
    _run_motors(motors, (Sequences.UNLOCK,) * len(motors))


def board_setup(mode: str) -> None:
    """
    Sets up board mode and motor pins. Mode is BOARD or BCM.
    """
    # Sets board mode
    if mode == "BOARD":
        GPIO.setmode(GPIO.BOARD)  # type: ignore
    elif mode == "BCM":
        GPIO.setmode(GPIO.BCM)  # type:ignore
    else:
        raise ValueError("Use 'BCM' or 'BOARD' modes.")


def board_cleanup() -> None:
    """
    Turns off any pins left on.
    """
    time.sleep(0.25)
    GPIO.cleanup()  # type: ignore


# Runs main only from command line call instead of library call
if __name__ == "__main__":
    main()
