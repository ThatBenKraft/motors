#!/usr/bin/env python
"""
# Stepper Driver
Allows for the control of a single stepper motor. step() function 
allows for customization of stepping sequence, direction, duration, and speed 
of motor. Includes a full and half-step sequence as well as single or offset 
stepping options.
"""
import copy
import time
from threading import Thread

import RPi.GPIO as GPIO

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "MIT"
__version__ = "1.3"
__maintainer__ = "Ben Kraft"
__email__ = "benjamin.kraft@tufts.edu"
__status__ = "Prototype"


MINIMUM_STEP_DELAY = 0.005


# Defines motor spin directions
class Directions:
    """
    Establishes existing motor directions.
    """

    CLOCKWISE = 1
    COUNTER_CLOCKWISE = -1


class Sequence:
    """
    A class for stepper motor sequences. Consist of 4-integer motor "stages".
    """

    def __init__(
        self,
        stages: list[tuple[int, int, int, int]],
        step_size: int = 1,
    ) -> None:
        # Assigns members
        self.stages = stages
        self.step_size = step_size
        self.length = len(stages)

    def _orient(self, direction: int) -> None:
        """
        Orients sequence in direction.
        """
        self.stages = self.stages[::direction]

    def _fit_steps(self, num_steps: int) -> None:
        """
        Extends/restricts sequence to fit number of steps.
        """
        # Divides number of specified steps by number of steps in sequence
        multiplier, remainder = divmod(num_steps, (self.length // self.step_size))
        # Prints warning if needed
        if remainder:
            print(
                f"WARNING: Number of steps ({num_steps}) not factor of sequence ({len(self.stages)}). Future steps might mis-align."
            )
        remainder_stages = self.stages[: (remainder * self.step_size)]
        # Builds a long sequence from "multiplier" number of sequences and remainder
        self.stages = self.stages * multiplier + remainder_stages


class Sequences:
    """
    Establishes existing stepper motor sequences.
    """

    HALFSTEP = Sequence(
        stages=[
            (1, 0, 0, 0),
            (1, 1, 0, 0),
            (0, 1, 0, 0),
            (0, 1, 1, 0),
            (0, 0, 1, 0),
            (0, 0, 1, 1),
            (0, 0, 0, 1),
            (1, 0, 0, 1),
        ],
        step_size=2,
    )
    WHOLESTEP = Sequence(
        stages=[
            (1, 0, 0, 1),
            (1, 1, 0, 0),
            (0, 1, 1, 0),
            (0, 0, 1, 1),
        ]
    )
    LOCK = Sequence([(1, 0, 0, 1)])
    UNLOCK = Sequence([(0, 0, 0, 0)])


class Motor:
    """
    A class for stepper motors. Consists of four pins.
    """

    def __init__(self, pins: tuple[int, int, int, int]) -> None:
        # Checks number of pins
        if len(pins) != 4:
            raise ValueError("Motor must consist of four integer pins!")
        # Sets all motor pins to output and disengages them
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)  # type: ignore
            GPIO.output(pin, False)  # type: ignore
        # Creates member
        self.pins = pins

    def get_pin(self, index: int) -> int:
        return self.pins[index]


class _MotorThread(Thread):
    """
    Allows for motor objects to be used concurrently in threads. MotorThread
    can be passed any motor object, as well as a number of steps, a direction,
    a sequnce, and a delay. Optional flag to show start/stop of thread.
    """

    def __init__(
        self,
        motor: Motor,
        num_steps: int,
        direction: int = Directions.CLOCKWISE,
        sequence: Sequence = Sequences.WHOLESTEP,
        delay: float = MINIMUM_STEP_DELAY,
        flag: bool = False,
    ):
        Thread.__init__(self)
        self.motor = motor
        self.num_steps = num_steps
        self.direction = direction
        self.sequence = sequence
        self.delay = delay
        self.flag = flag

    def run(self):
        """
        Starts motor thread.
        """
        if self.flag:
            print(f"Starting {self.name}. . .")
        step_motor(
            self.motor,
            self.num_steps,
            self.direction,
            self.sequence,
            self.delay,
        )
        if self.flag:
            print(f"Stopping {self.name}. . .")


def step_motors(
    motors: list[Motor],
    num_steps: list[int],
    directions: list[int],
    sequence: Sequence = Sequences.HALFSTEP,
    delay: float = MINIMUM_STEP_DELAY,
    flag: bool = False,
) -> None:
    """
    Allows for motors to run a specified number of steps to be run in a
    direction using a sequence of custom delay.
    """
    # Counts the number of motors being used
    num_motors = len(motors)
    # Checks list lengths to be the same size
    if num_motors != len(directions) or num_motors != len(num_steps):
        raise ValueError(
            "Lists of motors, directions, and steps must all be of equal size!"
        )
    # Initializes threads list
    threads: list[_MotorThread] = []
    # For each motor:
    for i in range(num_motors):
        # Creates a thread for the motor
        thread = _MotorThread(
            motors[i],
            num_steps[i],
            directions[i],
            sequence,
            delay,
            flag,
        )
        # Adds thread to list
        threads.append(thread)
        # Starts thread
        thread.start()
    # Displays start of threads
    if flag:
        print("All motor threads started.")
    # For each thread:
    for thread in threads:
        # Wait for all threads to finish
        thread.join()
    # Displays end of threads
    if flag:
        print("All motor threads joined.")


def step_motor(
    motor: Motor,
    num_steps: int,
    direction: int,
    sequence: Sequence = Sequences.HALFSTEP,
    delay: float = MINIMUM_STEP_DELAY,
) -> None:
    """
    Allows for a specified number of steps to be run in a direction using a
    sequence of custom delay.
    """
    if abs(direction) != 1:
        raise ValueError("Direction must be equal to 1 or -1!")
    # Returns if delay is too small
    if delay < MINIMUM_STEP_DELAY:
        raise ValueError(
            f"Too small of delay. Must be equal to or larger than {MINIMUM_STEP_DELAY}s!"
        )
    # Returns early if there are no steps.
    if not num_steps:
        return
    # Flips direction if number of steps is negative
    elif num_steps < 0:
        direction *= -1
        num_steps *= -1
    # Makes a copy of the input sequence to manipulate
    adjusted_sequence = copy.copy(sequence)
    # Orients sequence
    adjusted_sequence._orient(direction)
    # Fits sequence to number of steps
    adjusted_sequence._fit_steps(num_steps)
    # For each stage in sequence
    for stage in adjusted_sequence.stages:
        # For each pin level in stage
        for pin_index, level in enumerate(stage):
            # Sets motor pin to specified level
            GPIO.output(motor.get_pin(pin_index), bool(level))  # type: ignore
        # Delays between stages
        time.sleep(delay)


def board_setup(mode: str = "BCM") -> None:
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
    GPIO.cleanup()  # type: ignore


# Runs main only from command line call instead of library call
if __name__ == "__main__":
    print("Use me as a library!")
