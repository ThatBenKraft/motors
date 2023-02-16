import time

import gpio_driver
import numpy as np
from apds import APDS
from dual_motor_threading import weighted_move

BASE_STEP_COUNT = 4

WHITE = (430, 370, 320, 960)

RED = (140, 20, 40, 150)
BLACK = (5, 5, 5, 10)
PURPLE = (20, 25, 35, 65)

K_P = 0.05


def main():

    gpio_driver.pin_setup("BCM")
    sensor = APDS()

    ON_COLOR = RED

    RIGHT_TURN_WEIGHT = 1
    LEFT_TURN_WEIGHT = 4

    try:

        direction_weight = BASE_STEP_COUNT

        while True:

            color = sensor.get_color()
            print(f"Adjusted color: {color}")

            color_error = find_error(color, ON_COLOR) * K_P

            print(f"On Color Error: {color_error}")

            # GUIDES RIGHT
            if color_error > 30:
                direction_weight += RIGHT_TURN_WEIGHT
            # GUIDES LEFT
            # elif on_color_error < off_color_error:
            elif color_error < 5:
                direction_weight -= LEFT_TURN_WEIGHT

            LOW_LIMIT = int(BASE_STEP_COUNT * 0.7)
            HIGH_LIMIT = int(BASE_STEP_COUNT * 1.3)

            if direction_weight < LOW_LIMIT:
                direction_weight = LOW_LIMIT
            elif direction_weight > HIGH_LIMIT:
                direction_weight = HIGH_LIMIT

            print(f"Direction Weight: {direction_weight}")

            step_nums = (direction_weight, 2 * BASE_STEP_COUNT - direction_weight)

            print(f"Step nums: {step_nums}")

            time.sleep(0.1)

            weighted_move((step_nums)[::-1], delay=0.01)

    except KeyboardInterrupt:

        gpio_driver.pin_cleanup()


def normalize(color: tuple[int, int, int, int]):
    array = np.array(color)
    return array / max(array)


def find_error(color, base) -> float:

    sum = 0
    for i in range(len(color)):
        # Finds difference between colors
        difference = base[i] - color[i]
        # Adds to sum
        sum += abs(difference)
    # Returns the sum of the absolute value of each difference
    return round(sum, 3)


def at_limits(step_nums) -> bool:

    for num in step_nums:
        if num <= BASE_STEP_COUNT * 0.5 or num >= BASE_STEP_COUNT * 1.5:
            return True

    return False


if __name__ == "__main__":
    main()
