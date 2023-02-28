#!/usr/bin/env python
# dual_motor_threading.py
"""
Allows for motor objects to be used concurrently in threads. MotorThread can be
passed any motor object, as well as directions, delay, and number of steps.
Includes method weighted_move() to create two threads with custom step numbers.
"""
import threading
from threading import Thread

import gpio_driver
from gpio_driver import (
    MINIMUM_STEP_DELAY,
    Direction,
    Directions,
    Motor,
    Sequence,
    Sequences,
)

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "MIT"
__version__ = "1.0"
__maintainer__ = "Ben Kraft"
__email__ = "benjamin.kraft@tufts.edu"
__status__ = "Prototype"

# BOARD Mode pin setup
# gpio_driver.board_setup("BOARD")
# LEFT_MOTOR = Motor(11, 12, 13, 15)
# RIGHT_MOTOR = Motor(29, 31, 32, 33)
# BCM Mode pin setup
gpio_driver.board_setup("BCM")
RIGHT_MOTOR = Motor(17, 18, 27, 22)
LEFT_MOTOR = Motor(5, 6, 12, 13)


class MotorThread(Thread):
    """
    Allows for motors to be run in parallel using threading.
    """

    def __init__(
        self,
        motor: Motor,
        direction: Direction,
        num_steps: int,
        sequence: Sequence = Sequences.WHOLESTEP,
        delay: float = MINIMUM_STEP_DELAY * 2,
    ):
        threading.Thread.__init__(self)
        self.motor = motor
        self.direction = direction
        self.num_steps = num_steps
        self.sequence = sequence
        self.delay = delay

    def run(self):
        """
        Starts motor thread.
        """
        # print("Starting " + str(self.name))
        gpio_driver.step(
            (self.motor,),
            (self.direction,),
            self.num_steps,
            self.sequence,
            self.delay,
        )
        # print("Exiting " + str(self.name))


def weighted_move(
    num_steps: tuple[int, int], delay: float = MINIMUM_STEP_DELAY * 2
) -> None:
    """
    Runs motor threads with number of steps.
    """
    # Defines motor threads

    left_direction = Directions.CLOCKWISE
    if num_steps[0] < 0:
        num_steps = num_steps[0] * -1, num_steps[1]
        left_direction = Directions.COUNTER_CLOCKWISE

    right_direction = Directions.COUNTER_CLOCKWISE
    if num_steps[1] < 0:
        num_steps = num_steps[0], -1 * num_steps[1]
        right_direction = Directions.CLOCKWISE

    LEFT_MOTOR_THREAD = MotorThread(
        LEFT_MOTOR, left_direction, num_steps[0], delay=delay
    )
    RIGHT_MOTOR_THREAD = MotorThread(
        RIGHT_MOTOR, right_direction, num_steps[1], delay=delay
    )
    # Starts threads
    LEFT_MOTOR_THREAD.start()
    RIGHT_MOTOR_THREAD.start()
    # Waits for threads to end
    LEFT_MOTOR_THREAD.join()
    RIGHT_MOTOR_THREAD.join()


def main():
    pass


if __name__ == "__main__":
    main()
