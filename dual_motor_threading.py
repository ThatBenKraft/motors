import threading
import time
from threading import Thread

import gpio_driver
import RPi.GPIO as GPIO
from gpio_driver import MINIMUM_STEP_DELAY, Direction, Directions, Motor

# gpio_driver.pin_setup("BCM")
# Pin NUMBERS
# LEFT_MOTOR = Motor(11, 12, 13, 15)
# RIGHT_MOTOR = Motor(29, 31, 32, 33)
# BCM Pin NAMES
LEFT_MOTOR = Motor(17, 18, 27, 22)
RIGHT_MOTOR = Motor(5, 6, 12, 13)

MOTORS = (LEFT_MOTOR, RIGHT_MOTOR)


class MotorThread(Thread):
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

        time.sleep(1)

        print("Starting " + str(self.name))

        gpio_driver.step(
            (self.motor,), (self.direction,), self.num_steps, delay=self.delay
        )

        print("Exiting " + str(self.name))


def weighted_move(
    num_steps: tuple[int, int], delay: float = MINIMUM_STEP_DELAY * 2
) -> None:
    """
    Runs motor threads with number of steps.
    """
    # Defines a number of seconds in which the steps will take place
    MOVE_TIME = 1

    # for index, thread in enumerate(MOTOR_THREADS):
    #     thread.num_steps = num_steps[index]
    #     thread.delay = MOVE_TIME / num_steps[index]

    # LEFT_MOTOR_THREAD.delay = MOVE_TIME / num_steps[0]
    # RIGHT_MOTOR_THREAD.delay = MOVE_TIME / num_steps[1]

    LEFT_MOTOR_THREAD = MotorThread(
        LEFT_MOTOR, Directions.COUNTER_CLOCKWISE, num_steps[0], delay=delay
    )
    RIGHT_MOTOR_THREAD = MotorThread(
        RIGHT_MOTOR, Directions.CLOCKWISE, num_steps[1], delay=delay
    )

    LEFT_MOTOR_THREAD.start()
    RIGHT_MOTOR_THREAD.start()

    while True:
        if threading.active_count() == 1:
            break


# gpio_driver.step(
#     motors=MOTORS,
#     directions=(Directions.COUNTER_CLOCKWISE, Directions.CLOCKWISE),
#     num_steps=25,
#     delay=MINIMUM_STEP_DELAY,
# )


# time.sleep(1)
# weighted_move((200, 200))


# time.sleep(1)
# print("what")

# weighted_move((200, 200))
