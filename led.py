import gpio_driver
import RPi.GPIO as GPIO

gpio_driver.board_setup("BCM")

LED_PIN = 24
GPIO.setup(LED_PIN, GPIO.OUT)  # type: ignore


def on(pin: int = LED_PIN) -> None:
    """
    Turns on LED.
    """
    GPIO.output(pin, True)  # type: ignore


def off(pin: int = LED_PIN) -> None:
    """
    Turns off LED.
    """
    GPIO.output(pin, False)  # type: ignore
