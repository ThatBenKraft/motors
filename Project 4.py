import time

import gpio_driver
from gpio_driver import Directions, Motor, Sequences

gpio_driver.pin_setup()

MOTORS = (Motor(11, 12, 13, 15), Motor(29, 31, 32, 33))

num_steps = 20


# time.sleep(1)
gpio_driver.step(
    MOTORS,
    (Directions.CLOCKWISE, Directions.COUNTER_CLOCKWISE),
    Sequences.HALFSTEP,
    num_steps,
)

gpio_driver.pin_cleanup()


# gpio_driver.step(200, Sequences.WHOLESTEP, Directions.CLOCKWISE, delay=0.01)
# gpio_driver.pin_cleanup()
