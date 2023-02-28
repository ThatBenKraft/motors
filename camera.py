# Core opencv code provided by Einsteinium Studios
# Revisions to work with Pi Camera v3 by Briana Bouchard and Kenneth Siu

import time

import cv2
import gpio_driver
import numpy as np
import RPi.GPIO as GPIO
from libcamera import controls
from picamera2 import Picamera2

picam = Picamera2()  # assigns camera variable
picam.set_controls({"AfMode": controls.AfModeEnum.Continuous})  # sets auto focus mode
picam.start()  # activates camera


FULL_WIDTH = 640
FULL_HEIGHT = 480

CROP_WIDTH = 640
CROP_HEIGHT = 50

X_OFFSET = (FULL_WIDTH - CROP_WIDTH) // 2
Y_OFFSET = (FULL_HEIGHT - CROP_HEIGHT) // 2

CENTER_CROP_POSITION = (CROP_WIDTH // 2, CROP_HEIGHT // 2)


gpio_driver.board_setup("BCM")
LED_PIN = 24
GPIO.setup(LED_PIN, GPIO.OUT)  # type: ignore
GPIO.output(LED_PIN, True)  # type: ignore


def main() -> None:

    time.sleep(1)

    while True:

        print(find_line(monitor_display=True))

        time.sleep(0.1)


def find_line(monitor_display: bool = False) -> tuple[int, int]:
    """
    Finds blue line from camera and returns position. Optional flag to display
    camera output.
    """
    # Display camera input
    image = picam.capture_array("main")

    # Crop the image
    cropped_image = image[
        Y_OFFSET : (Y_OFFSET + CROP_HEIGHT),
        X_OFFSET : (X_OFFSET + CROP_WIDTH),
    ]

    # Convert to HUE SATURATION VALUES
    blue_colorspace = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)
    # COLOR RANGE
    LOW_BLUE = np.array((0, 25, 0))
    HIGH_BLUE = np.array((20, 255, 255))
    # Masks image based on defined blue values
    image_mask = cv2.inRange(blue_colorspace, LOW_BLUE, HIGH_BLUE)
    # Gaussian blur
    blurred_mask = cv2.GaussianBlur(image_mask, (5, 5), 0)
    # Find the contours of the masked area
    contours, _ = cv2.findContours(blurred_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # Returns early if no contours
    if len(contours) <= 0:
        print("No contours!")
        return 0, 0

    # Finds the biggest contour
    candidate = max(contours, key=cv2.contourArea)
    M = cv2.moments(candidate)  # determine moment - weighted average of intensities
    # Determines center positions
    if int(M["m00"]) == 0:
        center_x, center_y = CENTER_CROP_POSITION
    else:
        center_x = int(M["m10"] / M["m00"])  # find x component of centroid location
        center_y = int(M["m01"] / M["m00"])  # find y component of centroid location

    if monitor_display:
        # Displays full resolution image
        cv2.imshow("Raw Image", image)
        # Draws center lines
        cv2.line(cropped_image, (center_x, 0), (center_x, CROP_HEIGHT), (255, 0, 0), 1)
        cv2.line(cropped_image, (0, center_y), (CROP_WIDTH, center_y), (255, 0, 0), 1)
        # Draws contours
        cv2.drawContours(
            cropped_image, contours, -1, (0, 255, 0), 2
        )  # display green lines for all contours
        # Displays the resulting cropped frame
        cv2.imshow("Cropped Image", cropped_image)
        # Makes it work idk missing this thing had us banging our heads for an hour
        cv2.waitKey(1)

    # Returns difference between centroid components and center of screen
    return (
        center_x - CENTER_CROP_POSITION[0],
        center_y - CENTER_CROP_POSITION[1],
    )


if __name__ == "__main__":
    main()
