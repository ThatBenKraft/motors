import time

import gpio_driver
import numpy as np
from apds import APDS
from dual_motor_threading import weighted_move

# Establishes color tones
WHITE = (430, 370, 320, 960)
RED = (140, 20, 40, 150)
BLACK = (5, 5, 5, 10)
PURPLE = (20, 25, 35, 65)
BLUE = ()

K_P = 0.05


def main():

    gpio_driver.board_setup("BCM")
    sensor = APDS()

    ON_COLOR = RED

    RIGHT_TURN_WEIGHT = 1
    LEFT_TURN_WEIGHT = 4

    BASE_STEP_COUNT = 4

    # Defines correctional limits
    LOW_CORRECT_LIMIT = int(BASE_STEP_COUNT * 0.7)
    HIGH_CORRECT_LIMIT = int(BASE_STEP_COUNT * 1.3)

    try:

        step_weights = BASE_STEP_COUNT

        while True:
            # Acquires color data from sensor
            color = sensor.get_color()
            print(f"Adjusted color: {color}")
            # Finds error from correct color
            color_error = find_error(color, ON_COLOR) * K_P
            print(f"Color Error: {color_error}")
            # RIDES LEFT SIDE OF LINE
            # Guides right if error is high
            if color_error > 30:
                step_weights += RIGHT_TURN_WEIGHT
            # Guides left if color error is low
            elif color_error < 15:
                step_weights -= LEFT_TURN_WEIGHT

            # Corrects out-of-range values
            if step_weights < LOW_CORRECT_LIMIT:
                step_weights = LOW_CORRECT_LIMIT
            elif step_weights > HIGH_CORRECT_LIMIT:
                step_weights = HIGH_CORRECT_LIMIT
            print(f"Step Weights: {step_weights}")
            # Converts weights into discrete step values
            step_nums = (step_weights, 2 * BASE_STEP_COUNT - step_weights)
            print(f"Step nums: {step_nums}")

            time.sleep(0.1)
            # Moves
            weighted_move((step_nums)[::-1], delay=0.01)

    except KeyboardInterrupt:

        gpio_driver.board_cleanup()


def find_error(color: tuple[int, ...], base: tuple[int, ...]) -> float:
    """
    Finds an error value between the base and provided color.
    """
    sum = 0
    for i in range(len(color)):
        # Finds difference between colors
        difference = base[i] - color[i]
        # Adds to sum
        sum += abs(difference)
    # Returns the sum of the absolute value of each difference
    return round(sum, 3)


if __name__ == "__main__":
    main()
