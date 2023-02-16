import threading
import time
from threading import Thread

import apds
import gpio_driver
import RPi.GPIO as GPIO
from gpio_driver import MINIMUM_STEP_DELAY, Direction, Directions, Motor

GPIO.setmode(GPIO.BCM)  # type:ignore
# gpio_driver.pin_setup("BCM")
# Pin NUMBERS
# LEFT_MOTOR = Motor(11, 12, 13, 15)
# RIGHT_MOTOR = Motor(29, 31, 32, 33)
# BCM Pin NAMES
LEFT_MOTOR = Motor(17, 18, 27, 22)
RIGHT_MOTOR = Motor(5, 6, 12, 13)

MOTORS = (LEFT_MOTOR, RIGHT_MOTOR)


THREAD_STEP_DEFAULT = 10


class MotorThread(Thread):
    def __init__(
        self, motor: Motor, direction: Direction, delay: float = MINIMUM_STEP_DELAY
    ):
        threading.Thread.__init__(self)
        self.motor = motor
        self.direction = direction
        self.delay = delay
        self.num_steps = THREAD_STEP_DEFAULT

    def run(self):

        print("Starting " + str(self.name))

        gpio_driver.step((self.motor,), (self.direction,), self.num_steps)

        print("Exiting " + str(self.name))


LEFT_MOTOR_THREAD = MotorThread(
    LEFT_MOTOR,
    Directions.CLOCKWISE,
)
RIGHT_MOTOR_THREAD = MotorThread(
    RIGHT_MOTOR,
    Directions.COUNTER_CLOCKWISE,
)
MOTOR_THREADS = (LEFT_MOTOR_THREAD, RIGHT_MOTOR_THREAD)


def weighted_move(num_steps: tuple[int, int]) -> None:
    """
    Runs motor threads with number of steps.
    """
    # Defines a number of seconds in which the steps will take place
    MOVE_TIME = 1

    for index, thread in enumerate(MOTOR_THREADS):
        thread.num_steps = num_steps[index]
        thread.delay = MOVE_TIME / num_steps[index]

    LEFT_MOTOR_THREAD.start()
    RIGHT_MOTOR_THREAD.start()


# gpio_driver.step(
#     motors=MOTORS,
#     directions=(Directions.COUNTER_CLOCKWISE, Directions.CLOCKWISE),
#     num_steps=200,
#     delay=MINIMUM_STEP_DELAY,
# )


weighted_move((26, 25))

gpio_driver.pin_cleanup()
