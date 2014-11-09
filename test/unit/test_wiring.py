from setup_test import setup_test 
setup_test()

import unittest
import logging

from wiring import Wiring
from globe import Globe
from track import Tracker
from sensors import Sensors
from navigator import Navigator

class TestWiring(unittest.TestCase):

    def setUp(self):
        self.wiring = Wiring()
        
    def test_should_return_singleton_globe(self):
        globe = self.wiring.globe()
        self.assertEqual(globe, self.wiring.globe())
        self.assertTrue(isinstance(globe, Globe))
