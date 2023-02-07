#!/usr/bin/env python
"""
Allows for the control of a single stepper motor. step() function 
allows for customization of stepping sequence, direction, duration, and speed 
of motor. Includes a full and half-step sequence as well as single or offset 
stepping options.
"""
import time
from enum import Enum

import RPi.GPIO as GPIO

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "MIT"
__version__ = "1.1"
__maintainer__ = "Ben Kraft"
__email__ = "benjamin.kraft@tufts.edu"
__status__ = "Prototype"


# Defines motor spins
class Direction(Enum):
    CLOCKWISE = 1
    COUNTER_CLOCKWISE = -1


# Defines a "Sequence" type
class Sequence:
    def __init__(self, stages: tuple[tuple[int, ...], ...]) -> None:
        self.stages = stages

    def get_oriented(self, direction: Direction) -> tuple[tuple[int, ...], ...]:
        return self.stages[:: direction.value]


# Establishes stepper sequences
class Sequences:
    HALFSTEP = Sequence(
        (
            (1, 0, 0, 0),
            (1, 1, 0, 0),
            (0, 1, 0, 0),
            (0, 1, 1, 0),
            (0, 0, 1, 0),
            (0, 0, 1, 1),
            (0, 0, 0, 1),
            (1, 0, 0, 1),
        )
    )
    WHOLESTEP = Sequence(
        (
            (1, 0, 0, 1),
            (1, 1, 0, 0),
            (0, 1, 1, 0),
            (0, 0, 1, 1),
        )
    )
    LOCK = Sequence(((1, 0, 0, 1),))
    UNLOCK = Sequence(((0, 0, 0, 0),))


MINIMUM_STEP_DELAY = 0.005

MOTOR = (11, 12, 13, 15)


def main() -> None:
    """
    Runs main program actions.
    """
    start_time = time.time()

    try:
        pin_setup()
        # Sequence of motor actions
        lock_motor()
        time.sleep(1)
        step(200, Sequences.HALFSTEP, Direction.COUNTER_CLOCKWISE)
        lock_motor()
        time.sleep(5)

    except KeyboardInterrupt:
        # Turns off pins left on
        pin_cleanup()
    # Turns off pins left on
    pin_cleanup()
    # Calculates and reports execution time
    elapsed_time = round((time.time() - start_time), 3)
    print("Execution time:", elapsed_time, "seconds")


def step(
    num_steps: int = 1,
    sequence: Sequence = Sequences.HALFSTEP,
    direction: Direction = Direction.CLOCKWISE,
    delay: float = MINIMUM_STEP_DELAY * 2,
) -> None:
    """
    Allows for a specified number of steps to be run in a direction using a
    sequence of custom delay.
    """
    # Defines number of steps within any given sequence
    SEQUENCE_STEPS = 4
    # Defines number of stages per step in sequence
    step_length = len(sequence.stages) // SEQUENCE_STEPS
    # Finds quotient and remainder from steps
    quotient, remainder = divmod(num_steps, SEQUENCE_STEPS)
    # Prints warning
    if remainder:
        print("WARNING: Steps not factor of 8. Future steps might mis-align.")
    # Re-arranges sequence if specified
    base_stages = sequence.get_oriented(direction)
    # Creates a short sequence from remaining steps
    short_stages = base_stages[: (remainder * step_length)]
    # Builds a long sequence from "quotient" number of sequences and remainder
    combined_stages = base_stages * quotient + short_stages
    # Runs motor with custom sequence
    _run_motor(Sequence(combined_stages), (delay / step_length))


def _run_motor(sequence: Sequence, delay: float = MINIMUM_STEP_DELAY) -> None:
    """
    Controls motor to execute sequence using delay.
    """
    # Raises error for too small delay
    if delay < MINIMUM_STEP_DELAY:
        raise ValueError(
            f"Too small of delay. Must be equal to or larger than {MINIMUM_STEP_DELAY}s."
        )
    # For each stage in sequence:
    for stage in sequence.stages:
        # For each pin in stage
        for pin, level in enumerate(stage):
            # Sets motor pin to specified level
            GPIO.output(MOTOR[pin], level)  # type: ignore
        # Delays between stages
        time.sleep(delay)


def lock_motor() -> None:
    """
    Runs a constant signal on the motor. WARNING: Do not keep on.
    """
    # Runs first step of sequence to lock the motor
    _run_motor(Sequences.LOCK)


def unlock_motor() -> None:
    """
    Turns off all motor pins.
    """
    # Turns off all pins to motor
    _run_motor(Sequences.UNLOCK)


def pin_setup() -> None:
    """
    Sets up board mode and motor pins.
    """
    # Sets board mode
    GPIO.setmode(GPIO.BOARD)  # type: ignore
    # Sets all motor pins to output and disengages them
    for pin in MOTOR:
        GPIO.setup(pin, GPIO.OUT)  # type: ignore
        GPIO.output(pin, False)  # type: ignore


def pin_cleanup() -> None:
    """
    Turns off any pins left on.
    """
    time.sleep(0.25)
    GPIO.cleanup()  # type: ignore


# Runs main only from command line call instead of library call
if __name__ == "__main__":
    main()
