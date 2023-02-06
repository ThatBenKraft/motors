#!/usr/bin/env python
"""
Provides control for a stepper-motor setup. Allows for two-directional 
movement and rotation at varying speeds. Allows for use of `step()`, to shift 
motor individual or multiple steps.
functions.
"""
import time

import RPi.GPIO as GPIO

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Ben Kraft"
__email__ = "benjamin.kraft@tufts.edu"
__status__ = "Prototype"

# Establishes stepper sequences
HALFSTEP_SEQUENCE = (
    (1, 0, 0, 0),
    (1, 1, 0, 0),
    (0, 1, 0, 0),
    (0, 1, 1, 0),
    (0, 0, 1, 0),
    (0, 0, 1, 1),
    (0, 0, 0, 1),
    (1, 0, 0, 1),
)

WHOLESTEP_SEQUENCE = (
    (1, 0, 0, 1),
    (1, 1, 0, 0),
    (0, 1, 1, 0),
    (0, 0, 1, 1),
)

LOCK_SEQUENCE = ((1, 0, 0, 1),)
UNLOCK_SEQUENCE = ((0, 0, 0, 0),)

MOTOR = (11, 12, 13, 15)

# Defines motor spins
CLOCKWISE = 1
COUNTER_CLOCKWISE = -1

MINIMUM_STEP_DELAY = 0.005


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
        step(200, HALFSTEP_SEQUENCE, COUNTER_CLOCKWISE)
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
    sequence: tuple[tuple[int, ...], ...] = HALFSTEP_SEQUENCE,
    direction: int = CLOCKWISE,
    delay: float = MINIMUM_STEP_DELAY * 2,
) -> None:
    """
    Allows for a specified number of steps to be run in a direction using a
    sequence of custom delay.
    """
    # Defines number of steps within any given sequence
    SEQUENCE_STEPS = 4
    # Defines number of stages per step in sequence
    step_length = len(sequence) // SEQUENCE_STEPS
    # Finds quotient and remainder from steps
    quotient, remainder = divmod(num_steps, SEQUENCE_STEPS)
    # Prints warning
    if remainder:
        print("WARNING: Steps not factor of 8. Future steps might mis-align.")
    # Re-arranges sequence if specified
    new_sequence = sequence[::direction]
    # Creates a short sequence from remaining steps
    short_sequence = new_sequence[: (remainder * step_length)]
    # Builds a long sequence from "quotient" number of sequences and remainder
    long_sequence = new_sequence * quotient + short_sequence
    # Runs motor with custom sequence
    _run_motor(long_sequence, (delay / step_length))


def _run_motor(
    sequence: tuple[tuple[int, ...], ...], delay: float = MINIMUM_STEP_DELAY
) -> None:
    """
    Controls motor to execute sequence using delay.
    """
    # Raises error for too small delay
    if delay < MINIMUM_STEP_DELAY:
        raise ValueError(
            f"Too small of delay. Must be equal to or larger than {MINIMUM_STEP_DELAY}s."
        )
    # For each stage in sequence:
    for stage in sequence:
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
    _run_motor(LOCK_SEQUENCE)


def unlock_motor() -> None:
    """
    Turns off all motor pins.
    """
    # Turns off all pins to motor
    _run_motor(UNLOCK_SEQUENCE)


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
