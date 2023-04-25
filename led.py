"""
Allows for the use of any pin as an LED though an object.
"""

import RPi.GPIO as GPIO
import stepper

stepper.board_setup("BCM")

DEFAULT_PIN = 24


class LED:
    """
    Allows for the use of any pin as an LED.
    """

    def __init__(self, pin: int = DEFAULT_PIN) -> None:

        GPIO.setup(pin, GPIO.OUT)  # type: ignore
        self.pin = pin

    def on(self) -> None:
        """
        Turns on LED.
        """
        GPIO.output(self.pin, True)  # type: ignore

    def off(self) -> None:
        """
        Turns on LED.
        """
        GPIO.output(self.pin, False)  # type: ignore
