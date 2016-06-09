from setup_test import setup_test
setup_test()
import unittest

from simulate.simulated_vehicle import SimulatedWindSensor, INITIAL_WIND_DIRECTION

class TestSimulatedWindSensor(unittest.TestCase):

    def test_should_initially_return_constructor_wind_direction(self):
        wind_sensor = SimulatedWindSensor(10)
        self.assertEqual(10,wind_sensor.angle())

    def test_should_return_wind_direction_relative_to_vehicle_bearing_maintaining_abs_direction(self):
        wind_sensor = SimulatedWindSensor(10)

        wind_sensor.set_bearing(20)
        self.assertEqual(350, wind_sensor.angle())

        wind_sensor.set_bearing(350)
        self.assertEqual(20, wind_sensor.angle())
