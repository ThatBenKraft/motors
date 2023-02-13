import time

import gpio_driver
from gpio_driver import Directions, Motor, Sequence, Sequences

gpio_driver.pin_setup()

MOTOR_A = Motor(11, 12, 13, 15)
MOTOR_B = Motor(29, 31, 32, 33)
MOTORS = (MOTOR_A, MOTOR_B)

NUM_STEPS = 20

new_sequence: Sequence = Sequences.HALFSTEP
new_sequence.lengthen(NUM_STEPS)


# gpio_driver._run_motors(MOTORS, (new_sequence, new_sequence))
# time.sleep(1)
gpio_driver.steps(
    MOTORS, (Directions.CLOCKWISE, Directions.COUNTER_CLOCKWISE), num_steps=NUM_STEPS
)

gpio_driver.pin_cleanup()


# gpio_driver.step(200, Sequences.WHOLESTEP, Directions.CLOCKWISE, delay=0.01)
# gpio_driver.pin_cleanup()
