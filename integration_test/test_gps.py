from setup_test import setup_test
setup_test()

import unittest
import time

from gps_reader import GpsReader
from position import Position

class TestGps(unittest.TestCase):
    
    def setUp(self):
        self.gps_reader = GpsReader()
        self.gps_reader.start()
    
    def tearDown(self):
        self.gps_reader.running = False
        self.gps_reader.join()

    def test_should_return_hasfix_false_and_none_for_values_if_gps_has_no_fix(self):
        self.assertEqual(self.gps_reader.hasfix,False)
        self.assertEqual(self.gps_reader.position,None)
        self.assertEqual(self.gps_reader.heading,None)
        self.assertEqual(self.gps_reader.speed,None)
        self.assertEqual(self.gps_reader.time,None)

    def test_should_return_values_if_gps_has_fix(self):
        tries = 0
        while (not(self.gps_reader.hasfix) and tries < 100):
            tries = tries + 1
            time.sleep(0.1)
        self.assertLess(tries,100,"GPS failed to get fix within 10 seconds")
        self.assertEqual(self.gps_reader.hasfix,True)
        self.assertIsInstance(self.gps_reader.position,Position)
        self.assertGreater(self.gps_reader.heading,0)
        self.assertGreater(self.gps_reader.speed,0)
        self.assertGreater(self.gps_reader.time,0)
