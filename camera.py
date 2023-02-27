# Core opencv code provided by Einsteinium Studios
# Revisions to work with Pi Camera v3 by Briana Bouchard and Kenneth Siu

import time

import cv2
import numpy as np
from libcamera import controls
from picamera2 import Picamera2

picam = Picamera2()  # assigns camera variable
picam.set_controls({"AfMode": controls.AfModeEnum.Continuous})  # sets auto focus mode
picam.start()  # activates camera

Y_OFFSET = 60
Y_HEIGHT = 60

X_OFFSET = 0
X_WIDTH = 160

CENTER_POSITION = (X_WIDTH // 2, Y_HEIGHT // 2)


def main() -> None:

    while True:

        get_line_position(display=True)


def get_line_position(display: bool = False) -> tuple[int, int]:
    # Display camera input
    image = picam.capture_array("main")

    # Crop the image
    cropped_image = image[
        Y_OFFSET : (Y_OFFSET + Y_HEIGHT), X_OFFSET : (X_OFFSET + X_WIDTH)
    ]

    # Convert to HUE SATURATION VALUES
    Blue = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2HSV)

    # COLOR RANGE
    lower_blue = np.array([0, 25, 0])
    upper_blue = np.array([20, 255, 255])

    image_mask = cv2.inRange(Blue, lower_blue, upper_blue)

    # Gaussian blur
    blurred_mask = cv2.GaussianBlur(image_mask, (5, 5), 0)

    # Find the contours of the frame
    contours, _ = cv2.findContours(blurred_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # (if detected)
    if len(contours) <= 0:
        return 0, 0

    # Finds the biggest contour
    candidate = max(contours, key=cv2.contourArea)
    M = cv2.moments(candidate)  # determine moment - weighted average of intensities
    if int(M["m00"]) != 0:
        cx = int(M["m10"] / M["m00"])  # find x component of centroid location
        cy = int(M["m01"] / M["m00"])  # find y component of centroid location
    else:
        cx, cy = CENTER_POSITION

    if display:
        # Displays full resolution image
        cv2.imshow("image", image)

        cv2.line(
            cropped_image, (cx, 0), (cx, Y_HEIGHT), (255, 0, 0), 1
        )  # display vertical line at x value of centroid
        cv2.line(
            cropped_image, (0, cy), (X_WIDTH, cy), (255, 0, 0), 1
        )  # display horizontal line at y value of centroid

        cv2.drawContours(
            cropped_image, contours, -1, (0, 255, 0), 2
        )  # display green lines for all contours
        # Display the resulting cropped frame
        cv2.imshow("frame", cropped_image)

    # Returns difference between centroid components and center of screen
    return cx - CENTER_POSITION[0], cy - CENTER_POSITION[1]
