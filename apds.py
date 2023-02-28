import time

import board
import led
from adafruit_apds9960.apds9960 import APDS9960

I2C = board.I2C()


class APDS:
    """
    Allows for data acquisition with an APDS9960 sensor.
    """

    def __init__(self, enable_proximity: bool = True, enable_color: bool = True):
        self.sensor = APDS9960(I2C)
        self.sensor.enable_proximity = enable_proximity
        self.sensor.enable_color = enable_color
        self.sensor.color_gain = 1
        self.sensor.color_integration_time = 100
        self.get_color()

    def get_proximity(self) -> int:
        """
        Returns the proximity value from the connected sensor.
        """
        return self.sensor.proximity

    def get_color(self) -> tuple[int, int, int, int]:
        """
        Returns the RGBA values from the connected sensor.
        """
        return self.sensor.color_data


led.on()


def main() -> None:

    sensor = APDS()

    while True:
        try:
            print(f"Proximity: {sensor.get_proximity()}")
            print(f"Color: {sensor.get_color()}")
            time.sleep(0.5)
            # print("mode" + str(GPIO.getmode()))
        except KeyboardInterrupt:
            break


if __name__ == "__main__":
    main()
