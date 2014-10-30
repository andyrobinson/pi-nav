from setup_test import setup_test
setup_test()

import unittest

from fake_gps import FakeGPS
from sensors import Sensors

class TestSensors(unittest.TestCase):

	def setUp(self):
		self.gps = FakeGPS()
		self.sensors = Sensors(self.gps)

	def test_should_pass_through_gps_values(self):
		self.assertEqual(self.sensors.hasfix, self.gps.hasfix)
		self.assertEqual(self.sensors.position, self.gps.position)
		self.assertEqual(self.sensors.track, self.gps.track)
		self.assertEqual(self.sensors.speed, self.gps.speed)
		self.assertEqual(self.sensors.time, self.gps.time)
		self.assertEqual(self.sensors.speed_error, self.gps.speed_error)
		self.assertEqual(self.sensors.track_error, self.gps.track_error)

	def test_should_reflect_changes_in_gps_values(self):
		self.gps.hasfix = 'blah'
		self.assertEqual(self.sensors.hasfix,'blah')
