import math
import threading
import time
from enum import Enum
from threading import Thread

import gpio_driver
from apds import APDS
from gpio_driver import MINIMUM_STEP_DELAY, Direction, Directions, Motor

# gpio_driver.pin_setup()

SENSOR = APDS()
LEFT_MOTOR = Motor(11, 12, 13, 15)
RIGHT_MOTOR = Motor(29, 31, 32, 33)
MOTORS = (LEFT_MOTOR, RIGHT_MOTOR)


FORWARDS = (Directions.CLOCKWISE, Directions.COUNTER_CLOCKWISE)
BACKWARDS = (Directions.COUNTER_CLOCKWISE, Directions.CLOCKWISE)

TURN_LEFT = (Directions.COUNTER_CLOCKWISE, Directions.COUNTER_CLOCKWISE)
TURN_RIGHT = (Directions.CLOCKWISE, Directions.CLOCKWISE)

STEPS_PER_ROTATION = 200

WHEEL_RADIUS_MM = 100
TURNING_RADIUS_MM = 200


class Speed(Enum):
    """
    Speeds for motor delays.
    """

    FAST = MINIMUM_STEP_DELAY
    MEDIAL = MINIMUM_STEP_DELAY * 2
    SLOW = MINIMUM_STEP_DELAY * 4


def move_forwards(distance_mm: float, speed: Speed = Speed.MEDIAL) -> None:
    """
    Moves robot forwards custom amount and speed.
    """
    gpio_driver.step(
        motors=MOTORS,
        directions=FORWARDS,
        num_steps=distance_to_steps(distance_mm),
        delay=speed.value,
    )


def move_backwards(distance_mm: float, speed: Speed = Speed.MEDIAL) -> None:
    """
    Moves robot backwards custom amount and speed.
    """
    gpio_driver.step(
        motors=MOTORS,
        directions=BACKWARDS,
        num_steps=distance_to_steps(distance_mm),
        delay=speed.value,
    )


def turn_left(degrees=90, speed: Speed = Speed.MEDIAL) -> None:
    """
    Moves robot backwards custom amount and speed.
    """
    gpio_driver.step(
        motors=MOTORS,
        directions=TURN_LEFT,
        num_steps=degrees_to_steps(degrees),
        delay=speed.value,
    )


def turn_right(degrees=90, speed: Speed = Speed.MEDIAL) -> None:
    """
    Moves robot backwards custom amount and speed.
    """
    gpio_driver.step(
        motors=MOTORS,
        directions=TURN_RIGHT,
        num_steps=degrees_to_steps(degrees),
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


# while True:
#     time.sleep(1)
#     colors = SENSOR.get_color()
#     alpha = colors[3]
#     print(colors)
#     if alpha:
#         newList = [round(color / alpha, 3) for color in colors]
#         print(newList)


gpio_driver.board_cleanup()
