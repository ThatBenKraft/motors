#!/usr/bin/env python
# camera.py
"""
Acts as a basic PID controller for a dual-motor line-following robot. Does not
include path-finding or line-scouting (yet).
"""
import time

import camera
import stepper_driver
from dual_motor_controls import move_steps

__author__ = "Ben Kraft"
__copyright__ = "None"
__credits__ = "Ben Kraft"
__license__ = "MIT"
__version__ = "1.1"
__maintainer__ = "Ben Kraft"
__email__ = "benjamin.kraft@tufts.edu"
__status__ = "Prototype"

MIN_STEPS = 4
BASE_MOVE_COUNT = 2

# Defines proportional control constants
K_P = 0.01
K_I = 0.001
K_D = 0.001


def main() -> None:
    """
    Runs main PID actions.
    """
    stepper_driver.board_setup("BCM")
    # Defines variables for integral and derivative control
    previous_error = 0
    error_sum = 0

    while True:

        try:
            # Finds error from camera
            x_error, y_error, on_line = camera.find_line(False)
            print(f"X: {x_error}")
            # Calculates a proportional, integral, and derivative control error
            pid_value = int(
                (x_error * K_P) + (error_sum * K_I) + ((x_error - previous_error) * K_D)
            )
            # Updaetes values
            previous_error = x_error
            error_sum += x_error
            # Scales values to fit appropirate number of steps
            left_steps = (BASE_MOVE_COUNT + pid_value) * MIN_STEPS
            right_steps = (BASE_MOVE_COUNT - pid_value) * MIN_STEPS
            # Reports
            print(f"Number of Steps: L:{left_steps}, R:{right_steps}")

            time.sleep(0.1)
            # Moves motors appropriate amounts
            move_steps(left_steps, right_steps, delay=0.01)

        except KeyboardInterrupt:
            # Cleans up board
            stepper_driver.board_cleanup()
            break

    # gpio_driver.board_cleanup()


# def main():

#     gpio_driver.board_setup("BCM")
#     sensor = APDS()

#     ON_COLOR = RED

#     RIGHT_TURN_WEIGHT = 1
#     LEFT_TURN_WEIGHT = 4

#     BASE_STEP_COUNT = 4

#     # Defines correctional limits
#     LOW_CORRECT_LIMIT = int(BASE_STEP_COUNT * 0.7)
#     HIGH_CORRECT_LIMIT = int(BASE_STEP_COUNT * 1.3)

#     try:

#         step_weights = BASE_STEP_COUNT

#         while True:
#             # Acquires color data from sensor
#             color = sensor.get_color()
#             print(f"Adjusted color: {color}")
#             # Finds error from correct color
#             color_error = find_error(color, ON_COLOR) * K_P
#             print(f"Color Error: {color_error}")
#             # RIDES LEFT SIDE OF LINE
#             # Guides right if error is high
#             if color_error > 30:
#                 step_weights -= RIGHT_TURN_WEIGHT
#             # Guides left if color error is low
#             elif color_error < 15:
#                 step_weights += LEFT_TURN_WEIGHT

#             # Corrects out-of-range values
#             if step_weights < LOW_CORRECT_LIMIT:
#                 step_weights = LOW_CORRECT_LIMIT
#             elif step_weights > HIGH_CORRECT_LIMIT:
#                 step_weights = HIGH_CORRECT_LIMIT
#             print(f"Step Weights: {step_weights}")
#             # Converts weights into discrete step values
#             step_nums = (step_weights, 2 * BASE_STEP_COUNT - step_weights)
#             print(f"Step nums: {step_nums}")

#             time.sleep(0.1)
#             # Moves
#             weighted_move(step_nums, delay=0.01)

#     except KeyboardInterrupt:

#         gpio_driver.board_cleanup()


# def find_error(color: tuple[int, ...], base: tuple[int, ...]) -> float:
#     """
#     Finds an error value between the base and provided color.
#     """
#     # Finds number of channels
#     num_channels = range(len(base))
#     # Finds the differences between channels
#     differences = (abs(base[i] - color[i]) for i in num_channels)
#     # Sums the differences and rounds
#     return round(sum(differences), 3)


if __name__ == "__main__":
    main()
