import threading
import time
from threading import Thread

import gpio_driver
import RPi.GPIO as GPIO
from gpio_driver import MINIMUM_STEP_DELAY, Direction, Directions, Motor

# Pin NUMBERS
# gpio_driver.board_setup("BOARD")
# LEFT_MOTOR = Motor(11, 12, 13, 15)
# RIGHT_MOTOR = Motor(29, 31, 32, 33)
# BCM Pin NAMES
gpio_driver.board_setup("BCM")
LEFT_MOTOR = Motor(17, 18, 27, 22)
RIGHT_MOTOR = Motor(5, 6, 12, 13)


class MotorThread(Thread):
    """
    Allows for motors to be run in parallel using threading.
    """

    def __init__(
        self,
        motor: Motor,
        direction: Direction,
        num_steps: int,
        delay: float = MINIMUM_STEP_DELAY * 2,
    ):
        threading.Thread.__init__(self)
        self.motor = motor
        self.direction = direction
        self.delay = delay
        self.num_steps = num_steps

    def run(self):

        # print("Starting " + str(self.name))

        gpio_driver.step(
            (self.motor,), (self.direction,), self.num_steps, delay=self.delay
        )

        # print("Exiting " + str(self.name))


def weighted_move(
    num_steps: tuple[int, int], delay: float = MINIMUM_STEP_DELAY * 2
) -> None:
    """
    Runs motor threads with number of steps.
    """
    # Defines motor threads
    LEFT_MOTOR_THREAD = MotorThread(
        LEFT_MOTOR, Directions.COUNTER_CLOCKWISE, num_steps[0], delay=delay
    )
    RIGHT_MOTOR_THREAD = MotorThread(
        RIGHT_MOTOR, Directions.CLOCKWISE, num_steps[1], delay=delay
    )
    # Starts threads
    LEFT_MOTOR_THREAD.start()
    RIGHT_MOTOR_THREAD.start()
    # Waits for threads to end
    while True:
        if threading.active_count() == 1:
            break


def main():
    pass


if __name__ == "__main__":
    main()
