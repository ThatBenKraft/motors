import time
from enum import Enum

import gpio_driver
from gpio_driver import MINIMUM_STEP_DELAY, Directions, Motor, Sequences

gpio_driver.pin_setup()

MOTORS = (Motor(11, 12, 13, 15), Motor(29, 31, 32, 33))

FORWARDS = (Directions.CLOCKWISE, Directions.COUNTER_CLOCKWISE)
BACKWARDS = (Directions.COUNTER_CLOCKWISE, Directions.CLOCKWISE)

TURN_LEFT = (Directions.COUNTER_CLOCKWISE, Directions.COUNTER_CLOCKWISE)
TURN_RIGHT = (Directions.CLOCKWISE, Directions.CLOCKWISE)


class Speed(Enum):
    """
    Speeds for motor delays.
    """

    FAST = MINIMUM_STEP_DELAY
    MEDIAL = MINIMUM_STEP_DELAY * 2
    SLOW = MINIMUM_STEP_DELAY * 4


def move_forwards(num_steps: int, speed: Speed = Speed.MEDIAL) -> None:
    """
    Moves robot forwards custom amount and speed.
    """
    gpio_driver.step(
        motors=MOTORS,
        directions=FORWARDS,
        num_steps=num_steps,
        sequence=Sequences.HALFSTEP,
        delay=speed.value,
    )


def move_backwards(num_steps: int, speed: Speed = Speed.MEDIAL) -> None:
    """
    Moves robot backwards custom amount and speed.
    """
    gpio_driver.step(
        motors=MOTORS,
        directions=BACKWARDS,
        num_steps=num_steps,
        sequence=Sequences.HALFSTEP,
        delay=speed.value,
    )


move_forwards(400)

gpio_driver.pin_cleanup()
