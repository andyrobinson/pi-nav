from setup_test import setup_test
setup_test()

import unittest
import time

from gps_reader import GpsReader
from position import Position

def isnan(number):
    return str(number) == 'nan'

class TestGps(unittest.TestCase):
    
    def setUp(self):
        self.gps_reader = GpsReader()
        self.gps_reader.start()
    
    def tearDown(self):
        self.gps_reader.running = False
        self.gps_reader.join()

    def test_should_return_hasfix_false_and_NaN_for_values_if_gps_has_no_fix(self):
        self.assertEqual(self.gps_reader.hasfix,False)
        self.assertTrue(isnan(self.gps_reader.position.latitude))
        self.assertTrue(isnan(self.gps_reader.position.longitude))
        self.assertEqual(self.gps_reader.position.long_error,0)
        self.assertEqual(self.gps_reader.position.lat_error,0)
        self.assertTrue(isnan(self.gps_reader.track))
        self.assertTrue(isnan(self.gps_reader.speed))
        self.assertTrue(isnan(self.gps_reader.time))
        self.assertTrue(isnan(self.gps_reader.speed_error))
        self.assertTrue(isnan(self.gps_reader.track_error))

    def test_should_return_values_except_track_error_if_gps_has_fix(self):
        tries = 0
        while (not(self.gps_reader.hasfix) and tries < 100):
            tries = tries + 1
            time.sleep(0.1)
        self.assertLess(tries,100,"GPS failed to get fix within 10 seconds")
        self.assertEqual(self.gps_reader.hasfix,True)
        self.assertIsInstance(self.gps_reader.position,Position)
        self.assertGreater(self.gps_reader.position.latitude,0)
        self.assertLess(self.gps_reader.position.longitude,0)
        self.assertGreater(self.gps_reader.position.long_error,0)
        self.assertGreater(self.gps_reader.position.lat_error,0)
        self.assertGreater(self.gps_reader.track,0)
        self.assertGreater(self.gps_reader.speed,0)
        self.assertGreater(self.gps_reader.time,0)
        self.assertGreater(self.gps_reader.speed_error,0)
