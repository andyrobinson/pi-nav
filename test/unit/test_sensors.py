from setup_test import setup_test

setup_test()

import unittest

from simulate.stub_gps import StubGPS
from sensors import Sensors
from nan import NaN


class TestSensors(unittest.TestCase):
    def setUp(self):
        self.gps = StubGPS()
        self.sensors = Sensors(self.gps)

    def test_should_pass_through_gps_values(self):
        self.assertEqual(self.sensors.hasfix, self.gps.hasfix)
        self.assertEqual(self.sensors.position.latitude, self.gps.position.latitude)
        self.assertEqual(self.sensors.position.longitude, self.gps.position.longitude)
        self.assertEqual(self.sensors.position.lat_error, self.gps.position.lat_error)
        self.assertEqual(self.sensors.position.long_error, self.gps.position.long_error)
        self.assertEqual(self.sensors.track, self.gps.track)
        self.assertEqual(self.sensors.speed, self.gps.speed)
        self.assertEqual(self.sensors.time, self.gps.time)
        self.assertEqual(self.sensors.speed_error, self.gps.speed_error)
        self.assertEqual(self.sensors.track_error, self.gps.track_error)


    def test_should_reflect_changes_in_gps_values(self):
        self.gps.hasfix = 'blah'
        self.assertEqual(self.sensors.hasfix, 'blah')


    def test_should_default_error_values_to_ten_if_gps_returns_NaN(self):
        gps = StubGPS()
        gps.position.lat_error = NaN
        gps.position.long_error = NaN
        gps.speed_error = NaN
        gps.track_error = NaN

        sensors = Sensors(gps)

        self.assertEqual(sensors.position.lat_error, 10)
        self.assertEqual(sensors.position.long_error, 10)
        self.assertEqual(sensors.speed_error, 10)
        self.assertEqual(sensors.track_error, 10)


    def test_should_have_fixed_wind_drection(self):
        sensors = Sensors(StubGPS())
        self.assertEqual(sensors.wind_direction, 0)
