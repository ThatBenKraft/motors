#!/usr/bin/env python
# dual_motor_controls.py
"""
Allows for easy usage for a dual-motor robot. Assumes motor pin numbers, and 
creates directions as well as support for distance/degree movement.
"""
import math
from enum import Enum

import stepper
from stepper import Directions, Motor

# BOARD MOTORS
# LEFT_MOTOR = Motor(11, 12, 13, 15)
# RIGHT_MOTOR = Motor(29, 31, 32, 33)
# BCM MOTORS
LEFT_MOTOR = Motor(5, 6, 12, 13)
RIGHT_MOTOR = Motor(17, 18, 27, 22)
MOTORS = (LEFT_MOTOR, RIGHT_MOTOR)


FORWARDS = (Directions.CLOCKWISE, Directions.COUNTER_CLOCKWISE)
BACKWARDS = (Directions.COUNTER_CLOCKWISE, Directions.CLOCKWISE)

TURN_LEFT = (Directions.COUNTER_CLOCKWISE, Directions.COUNTER_CLOCKWISE)
TURN_RIGHT = (Directions.CLOCKWISE, Directions.CLOCKWISE)

STEPS_PER_ROTATION = 200

WHEEL_RADIUS_MM = 100
TURNING_RADIUS_MM = 200

BASE_DELAY = stepper.MINIMUM_STEP_DELAY
stepper.board_setup("BCM")


class Speed(Enum):
    """
    Speeds for motor delays.
    """

    FAST = BASE_DELAY
    MEDIAL = BASE_DELAY * 2
    SLOW = BASE_DELAY * 4


def move_steps(left_steps: int, right_steps: int, delay=BASE_DELAY):

    stepper.step_motors(
        motors=MOTORS,
        directions=FORWARDS,
        num_steps=(left_steps, right_steps),
        delay=delay,
    )


def move_forwards(distance_mm: float, speed: Speed = Speed.MEDIAL) -> None:
    """
    Moves robot forwards custom amount and speed.
    """
    stepper.step_motors(
        motors=MOTORS,
        directions=FORWARDS,
        num_steps=(distance_to_steps(distance_mm),) * 2,
        delay=speed.value,
    )


def move_backwards(distance_mm: float, speed: Speed = Speed.MEDIAL) -> None:
    """
    Moves robot forwards custom amount and speed.
    """
    stepper.step_motors(
        motors=MOTORS,
        directions=BACKWARDS,
        num_steps=(distance_to_steps(distance_mm),) * 2,
        delay=speed.value,
    )


def turn_left(degrees: float = 90, speed: Speed = Speed.MEDIAL) -> None:
    """
    Moves robot backwards custom amount and speed.
    """
    stepper.step_motors(
        motors=MOTORS,
        directions=TURN_LEFT,
        num_steps=(degrees_to_steps(degrees),) * 2,
        delay=speed.value,
    )


def turn_right(degrees: float = 90, speed: Speed = Speed.MEDIAL) -> None:
    """
    Moves robot backwards custom amount and speed.
    """
    stepper.step_motors(
        motors=MOTORS,
        directions=TURN_RIGHT,
        num_steps=(degrees_to_steps(degrees),) * 2,
        delay=speed.value,
    )


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


stepper.board_cleanup()
