import time

import gpio_driver
from gpio_driver import Directions, Sequences

time.sleep(1)
gpio_driver.pin_setup()
gpio_driver.step(200, Sequences.WHOLESTEP, Directions.CLOCKWISE, delay=0.01)
gpio_driver.pin_cleanup()
