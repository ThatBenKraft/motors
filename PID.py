import time

import gpio_driver
import numpy as np
import RPi.GPIO as GPIO
from apds import APDS
from dual_motor_threading import weighted_move

K_P = 1.2

BASE_STEP_COUNT = 8


LED_PIN = 24
# time.sleep(0.5)
GPIO.setup(LED_PIN, GPIO.OUT)  # type: ignore
GPIO.output(LED_PIN, True)  # type: ignore


def main():

    gpio_driver.pin_setup("BCM")

    RED = normalize(np.array((50, 20, 20)))

    # # HALF_RED = normalize(np.array((50, 20, 20)))
    # HALF_RED =
    HALF_RED = normalize(np.array((40, 20, 20)))

    step_nums = [BASE_STEP_COUNT, BASE_STEP_COUNT]
    sensor = APDS()

    LINE_MULTIPLIER = 4

    try:

        while True:

            raw_color = sensor.get_color()[:3]
            # print(f"Raw color: {raw_color}")
            color = normalize(np.array(raw_color))
            print(f"Adjusted color: {color}")

            red_error = find_error(color, RED)
            half_red_error = find_error(color, HALF_RED)

            print(f"Red Error: {red_error}\nHalf Red Error: {half_red_error}")

            if half_red_error < red_error:
                step_nums[0] += 1
                step_nums[1] -= 1
                # LEFT_MOTOR_THREAD.num_steps += 1
                # RIGHT_MOTOR_THREAD.num_steps -= 1
            elif half_red_error > red_error:
                step_nums[0] -= LINE_MULTIPLIER
                step_nums[1] += LINE_MULTIPLIER
                # LEFT_MOTOR_THREAD.num_steps -= LINE_MULTIPLIER
                # RIGHT_MOTOR_THREAD.num_steps += LINE_MULTIPLIER

            print(f"Step nums: {step_nums}")

            if step_nums[0] < BASE_STEP_COUNT * 0.75:
                step_nums = [int(BASE_STEP_COUNT * 0.75), int(BASE_STEP_COUNT * 1.25)]

            if step_nums[1] < BASE_STEP_COUNT * 0.75:
                step_nums = [int(BASE_STEP_COUNT * 1.75), int(BASE_STEP_COUNT * 0.25)]

            weighted_move(tuple(step_nums)[::-1])

            time.sleep(0.5)

    except KeyboardInterrupt:

        gpio_driver.pin_cleanup()


def normalize(color):
    return color / max(color)


def find_error(color, base):
    # Finds difference between colors
    difference = base - color
    # Returns the sum of the absolute value of each difference
    return sum(abs(color) for color in difference)


def at_limits(step_nums) -> bool:

    for num in step_nums:
        if num <= BASE_STEP_COUNT * 0.5 or num >= BASE_STEP_COUNT * 1.5:
            return True

    return False


if __name__ == "__main__":
    main()
