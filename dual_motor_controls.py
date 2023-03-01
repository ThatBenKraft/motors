#!/usr/bin/env python
# dual_motor_controls.py

import math
import time
from enum import Enum

import gpio_driver
from apds import APDS
from gpio_driver import Directions, Motor, StepThread

# gpio_driver.pin_setup()

SENSOR = APDS()
# BOARD MOTORS
# LEFT_MOTOR = Motor(11, 12, 13, 15)
# RIGHT_MOTOR = Motor(29, 31, 32, 33)
# BCM MOTORS
RIGHT_MOTOR = Motor(17, 18, 27, 22)
LEFT_MOTOR = Motor(5, 6, 12, 13)
MOTORS = (LEFT_MOTOR, RIGHT_MOTOR)


FORWARDS = (Directions.CLOCKWISE, Directions.COUNTER_CLOCKWISE)
BACKWARDS = (Directions.COUNTER_CLOCKWISE, Directions.CLOCKWISE)

TURN_LEFT = (Directions.COUNTER_CLOCKWISE, Directions.COUNTER_CLOCKWISE)
TURN_RIGHT = (Directions.CLOCKWISE, Directions.CLOCKWISE)

STEPS_PER_ROTATION = 200

WHEEL_RADIUS_MM = 100
TURNING_RADIUS_MM = 200

BASE_DELAY = gpio_driver.MINIMUM_STEP_DELAY
gpio_driver.board_setup("BCM")


class Speed(Enum):
    """
    Speeds for motor delays.
    """

    FAST = BASE_DELAY
    MEDIAL = BASE_DELAY * 2
    SLOW = BASE_DELAY * 4


def weighted_move(left_steps: int, right_steps: int, delay: float) -> None:
    """
    Runs motor threads with number of steps.
    """
    # Defines motor threads

    LEFT_MOTOR_THREAD = StepThread(
        LEFT_MOTOR,
        left_steps,
        Directions.CLOCKWISE,
        delay=delay,
    )
    RIGHT_MOTOR_THREAD = StepThread(
        RIGHT_MOTOR,
        right_steps,
        Directions.COUNTER_CLOCKWISE,
        delay=delay,
    )
    # Starts threads
    LEFT_MOTOR_THREAD.start()
    RIGHT_MOTOR_THREAD.start()
    # Waits for threads to end
    LEFT_MOTOR_THREAD.join()
    RIGHT_MOTOR_THREAD.join()


# def move_forwards(distance_mm: float, speed: Speed = Speed.MEDIAL) -> None:
#     """
#     Moves robot forwards custom amount and speed.
#     """
#     gpio_driver.step(
#         motors=MOTORS,
#         directions=FORWARDS,
#         num_steps=distance_to_steps(distance_mm),
#         delay=speed.value,
#     )


# def move_backwards(distance_mm: float, speed: Speed = Speed.MEDIAL) -> None:
#     """
#     Moves robot backwards custom amount and speed.
#     """
#     gpio_driver.step(
#         motors=MOTORS,
#         directions=BACKWARDS,
#         num_steps=distance_to_steps(distance_mm),
#         delay=speed.value,
#     )


# def turn_left(degrees=90, speed: Speed = Speed.MEDIAL) -> None:
#     """
#     Moves robot backwards custom amount and speed.
#     """
#     gpio_driver.step(
#         motors=MOTORS,
#         directions=TURN_LEFT,
#         num_steps=degrees_to_steps(degrees),
#         delay=speed.value,
#     )


# def turn_right(degrees=90, speed: Speed = Speed.MEDIAL) -> None:
#     """
#     Moves robot backwards custom amount and speed.
#     """
#     gpio_driver.step(
#         motors=MOTORS,
#         directions=TURN_RIGHT,
#         num_steps=degrees_to_steps(degrees),
#         delay=speed.value,
#     )


def distance_to_steps(distance_mm: float) -> int:
    """
    Converts moving distance to wheel steps.
    """
    return int(
        # Scales distance to wheel radians
        (distance_mm / WHEEL_RADIUS_MM)
        # Converts back to steps
        * (STEPS_PER_ROTATION / (2 * math.pi))
    )


def degrees_to_steps(degrees: float) -> int:
    """
    Converts turning radius degrees to wheel steps.
    """
    return int(
        # Scales degrees to wheel radius
        (TURNING_RADIUS_MM * degrees / WHEEL_RADIUS_MM)
        # Converts back to steps
        * (STEPS_PER_ROTATION / 360)
    )


# while True:
#     time.sleep(1)
#     colors = SENSOR.get_color()
#     alpha = colors[3]
#     print(colors)
#     if alpha:
#         newList = [round(color / alpha, 3) for color in colors]
#         print(newList)


gpio_driver.board_cleanup()
