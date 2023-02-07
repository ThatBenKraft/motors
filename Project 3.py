import time

import motor_driver
from motor_driver import Directions, Sequences

time.sleep(1)
motor_driver.pin_setup()
motor_driver.step(50, Sequences.HALFSTEP, Directions.COUNTER_CLOCKWISE)
motor_driver.pin_cleanup()
