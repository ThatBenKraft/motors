#!/usr/bin/env python
"""
## Stepper Driver
Allows for the control of a single stepper motor. step() function 
allows for customization of stepping sequence, direction, duration, and speed 
of motor. Includes a full and half-step sequence as well as single or offset 
stepping options.
"""

import time
from itertools import permutations
from threading import Thread

import RPi.GPIO as GPIO

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "MIT"
__version__ = "0.2.2"
__maintainer__ = "Ben Kraft"
__email__ = "ben.kraft@rcn.com"
__status__ = "Prototype"

STEPS_PER_REVOLUTION = 200

MINIMUM_STAGE_DELAY = 0.0015

DEFAULT_RPM = 60


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
        stages_per_step: int = 1,
    ) -> None:
        # Assigns members
        self.stages = stages
        self._num_stages = len(stages)
        self._stages_per_step = stages_per_step


class Sequences:
    """
    Establishes existing stepper motor sequences.
    """

    FULLSTEP = Sequence(
        stages=[
            (1, 0, 0, 1),
            (1, 1, 0, 0),
            (0, 1, 1, 0),
            (0, 0, 1, 1),
        ]
    )
    HALFSTEP = Sequence(
        stages=[
            (1, 0, 0, 1),
            (1, 0, 0, 0),
            (1, 1, 0, 0),
            (0, 1, 0, 0),
            (0, 1, 1, 0),
            (0, 0, 1, 0),
            (0, 0, 1, 1),
            (0, 0, 0, 1),
        ],
        stages_per_step=2,
    )
    WAVESTEP = Sequence(
        stages=[
            (1, 0, 0, 0),
            (0, 1, 0, 0),
            (0, 0, 1, 0),
            (0, 0, 0, 1),
        ]
    )
    LOCK = Sequence([(1, 0, 0, 1)])
    UNLOCK = Sequence([(0, 0, 0, 0)])


class Motor:
    """
    A class for stepper motors. Consists of four pin numbers.
    """

    def __init__(self, pins: tuple[int, int, int, int]) -> None:
        # Checks number of pins
        if len(pins) != 4:
            raise ValueError("Motor must consist of four integer pins!")
        # Sets all motor pins to output and disengages them
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)  # type: ignore
            GPIO.output(pin, False)  # type: ignore
        # Creates members
        self.pins = pins
        # Initializes variables for storing previous sequence
        self._sequence_index = -1
        self._sequence_length = 8

    def _get_scaled_index(self, sequence_length: int) -> int:
        """
        Gets index from previous run scaled up to new sequence length
        """
        return sequence_length * self._sequence_index // self._sequence_length

    def _set_index(self, index: int, sequence_length: int) -> None:
        """
        Sets new values for previous sequence length and index.
        """
        self._sequence_index = index
        self._sequence_length = sequence_length


class _MotorThread(Thread):
    """
    Allows for motor objects to be used concurrently in threads. `_MotorThread`
    can be passed any motor object, as well as a number of steps, a direction,
    a sequnce, and a delay. Optional flag to show start/stop of thread.
    """

    def __init__(
        self,
        motor: Motor,
        num_steps: float,
        direction: int,
        sequence: Sequence = Sequences.HALFSTEP,
        rpm: float = DEFAULT_RPM,
        flag_ends: bool = False,
    ):
        super().__init__()
        self.motor = motor
        self.num_steps = num_steps
        self.direction = direction
        self.sequence = sequence
        self.rpm = rpm
        self.flag_ends = flag_ends

    def run(self):
        """
        Starts motor thread.
        """
        try:
            if self.flag_ends:
                print(f"Starting {self.name}. . .")
            step_motor(
                self.motor,
                self.num_steps,
                self.direction,
                self.sequence,
                self.rpm,
            )
            if self.flag_ends:
                print(f"Stopping {self.name}. . .")
        except Exception as e:
            print(f"Thread {self.name} encountered an error: {e}")


def step_motors(
    motors: list[Motor],
    nums_steps: list[float],
    directions: list[int],
    sequence: Sequence = Sequences.HALFSTEP,
    rpm: float = DEFAULT_RPM,
    flag_ends: bool = False,
) -> None:
    """
    Allows for motors to run a specified number of steps to be run in a
    direction using a sequence of custom stage delay.
    """
    if not motors or not nums_steps or not directions:
        raise ValueError("Lists of motors, steps, and directions must not be empty!")
    # Counts the number of motors being used
    num_motors = len(motors)
    # Checks list lengths to be the same size
    if num_motors != len(directions) or num_motors != len(nums_steps):
        raise ValueError(
            "Lists of motors, directions, and steps must all be of equal size!"
        )
    # Initializes threads list
    threads: list[_MotorThread] = []
    # Walking through each element:
    for motor, num_steps, direction in zip(motors, nums_steps, directions):
        # Creates a thread for the motor
        thread = _MotorThread(motor, num_steps, direction, sequence, rpm, flag_ends)
        # Adds thread to list
        threads.append(thread)
        # Starts thread
        thread.start()
    # Displays start of threads
    if flag_ends:
        print("All motor threads started.")
    # For each thread:
    for thread in threads:
        # Wait for all threads to finish
        thread.join()
    # Displays end of threads
    if flag_ends:
        print("All motor threads joined.")


def step_motor(
    motor: Motor,
    num_steps: float,
    direction: int,
    sequence: Sequence = Sequences.HALFSTEP,
    rpm: float = DEFAULT_RPM,
) -> None:
    """
    Runs specified motor number of steps in direction. Optional sequence and
    RPM parameters.
    """
    if abs(direction) != 1:
        raise ValueError("Direction must be equal to 1 or -1!")
    # Calculates appropriate delay
    delay = _calculate_stage_delay(sequence, rpm)
    # Raises error if delay is too small
    if delay < MINIMUM_STAGE_DELAY:
        raise ValueError(
            f"Too large of an RPM. Stage delay must be equal to or larger than {MINIMUM_STAGE_DELAY}s!"
        )
    # Returns early if there are no steps.
    if not num_steps:
        return
    # Flips direction if number of steps is negative
    elif num_steps < 0:
        num_steps *= -1
        direction *= -1
    # Calcualtes number of stages from step size of sequence
    total_num_stages = float(num_steps * sequence._stages_per_step)
    # Warns if number of steps does not translate into stages
    if not total_num_stages.is_integer():
        print(
            f"WARNING: Number of steps does generate discrete number of stages. \
              Rounding {total_num_stages:.2f} to {round(total_num_stages)} steps."
        )
    # Makes a modified copy of the input sequence
    adjusted_sequence = _generate_sequence(
        motor, round(total_num_stages), direction, sequence
    )
    # Output adjusted sequence to motor
    _output_sequence(motor, adjusted_sequence, delay)
    # Unlocks motor pins
    unlock(motor)


def _output_sequence(motor: Motor, sequence, delay: float) -> None:
    # For each stage in sequence:
    for stage in sequence.stages:
        # For each pin level in stage:
        for index, level in enumerate(stage):
            # Sets motor pin to specified level
            GPIO.output(motor.pins[index], bool(level))  # type: ignore
        # Delays between stages
        time.sleep(delay)


def unlock(motor: Motor):
    """
    Sets all pins on motor to LOW.
    """
    _output_sequence(motor, Sequences.UNLOCK, 0)


def lock(motor: Motor):
    """
    Sets opposing coil pins on motor to HIGH.
    """
    _output_sequence(motor, Sequences.LOCK, 0)


def _generate_sequence(
    motor: Motor, total_num_stages: int, direction: int, sequence: Sequence
) -> Sequence:
    """
    Creates a custom sequences of specified length and direction for motor.
    Takes into account previous sequences.
    """
    # Gets sequence length
    sequence_length = sequence._num_stages
    # Calculates multiple and remainder between sequence and total stage counts.
    multiple, remainder = divmod(total_num_stages, sequence_length)
    # Orients stages according to direction
    oriented_stages = sequence.stages[::direction]
    # Acquires previous index from motor
    previous_index = motor._get_scaled_index(sequence_length)
    # Alters index based on direction
    # Needs to add or subtract 1 away from current index before shifting
    # Note: index for backwards = (sequence_length) - (previous_index - 1) - 1
    current_index = (
        previous_index + 1 if direction == 1 else sequence_length - previous_index
    )
    # Creates new stage palette shifted by index
    shifted_stages = oriented_stages[current_index:] + oriented_stages[:current_index]
    # Calculates new index from remainder and direction
    next_index = (previous_index + remainder * direction) % sequence_length
    # Stores sequence properties back in motor
    motor._set_index(next_index, sequence_length)
    # Creates a final sequence oriented and up to length
    total_stages = shifted_stages * multiple + shifted_stages[:remainder]
    # Returns new sequence object from stages and existing stages per step
    return Sequence(total_stages, sequence._stages_per_step)


def _calculate_stage_delay(sequence: Sequence, rpm: float) -> float:
    """
    Calculates delay from rpm and sequence attributes.
    """
    """
         rev      1 min     (STEPS_PER_REVOLUTION) steps     (step_size) stages
    x * ----- * -------- * ------------------------------ * --------------------
         min     60 sec                 1 rev                      1 step

       (x * STEPS_PER_REVOLUTION * step_size)   stages
    = ---------------------------------------- --------
                         60                       sec

                         60                       sec
    = ---------------------------------------- --------
       (x * STEPS_PER_REVOLUTION * step_size)   stages
    """
    return 60 / (rpm * STEPS_PER_REVOLUTION * sequence._stages_per_step)


def board_setup(mode: str = "BCM") -> None:
    """
    Sets up board mode and motor pins. Mode is BCM (GPIO pin numbers) or BOARD
    (processor pin numbers).
    """
    # Sets board mode
    if mode == "BCM":
        GPIO.setmode(GPIO.BCM)  # type:ignore
    elif mode == "BOARD":
        GPIO.setmode(GPIO.BOARD)  # type: ignore
    else:
        raise ValueError("Use 'BCM' or 'BOARD' modes.")


def board_cleanup() -> None:
    """
    Turns off any pins left on.
    """
    GPIO.cleanup()  # type: ignore


def test_pins(
    motor: Motor,
    num_steps: int = 0,
    sequence: Sequence = Sequences.HALFSTEP,
    delay: float = MINIMUM_STAGE_DELAY,
    spacing: float = 0.5,
) -> None:
    """
    Runs stepping sequence on all possible permutations of given pin list in
    order to find correct stepper wiring. Normal `step_motor()` arguments,
    `spacing` determines duration beween tests. `num_steps` is set to length
    of sequence if left at 0. Keyboard interupt will print last permutation.
    """
    # Sets number of steps to length of sequence if not specified
    if not num_steps:
        num_steps = sequence._num_stages
    # Creates a list of all possible pin permutations
    pin_permutations = list(permutations(motor.pins, 4))
    # Initializes a current order
    new_order: tuple[int, ...] = ()
    try:
        # For each permutation:
        for pin_order in pin_permutations:
            # Sets current order
            new_order = pin_order
            # Prints pin order
            print(f"Current permutation: {new_order}")
            # Creates new motor object
            new_motor = Motor(new_order)  # type: ignore
            # Runs motor for runtime
            step_motor(new_motor, num_steps, Directions.CLOCKWISE, sequence, delay)
            # Waits between permutations
            time.sleep(spacing)
    # Catches keyboard interupt
    except KeyboardInterrupt:
        # Reports last pin order
        print(f"\nLast pin permutation: {new_order}")


# Runs main only from command line call instead of library call
if __name__ == "__main__":
    print("Use me as a library!")
