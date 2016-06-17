from setup_test import setup_test
setup_test()

import unittest
import time

from windsensor import WindSensor
from i2c import I2C

ADDRESS_OF_SENSOR = 0x40

class TestWindSensor(unittest.TestCase):

    def setUp(self):
        sensor_i2c = I2C(ADDRESS_OF_SENSOR)
        self.sensor = WindSensor(sensor_i2c)

    def test_should_read_direction_between_0_and_360(self):
        wind_direction = self.sensor.angle
        self.assertGreater(angle,-0.01)
        self.assertLess(angle,360.0)
