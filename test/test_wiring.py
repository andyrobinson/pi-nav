from setup_test import setup_test
setup_test()

import unittest
import logging

from wiring import Wiring
from globe import Globe
from track import Tracker

class TestWiring(unittest.TestCase):

    def setUp(self):
        self.wiring = Wiring()
        
    def test_should_return_singleton_globe(self):
        globe = self.wiring.globe()
        self.assertEqual(globe, self.wiring.globe())
        self.assertTrue(isinstance(globe, Globe))

    def test_should_return_singleton_console_logger(self):
        logger = self.wiring.console_logger()
        self.assertEqual(logger, self.wiring.console_logger())
        self.assertTrue(isinstance(logger, logging.Logger))
        
    def test_should_return_a_tracker(self):
        tracker = self.wiring.tracker_simulator()
        self.assertTrue(isinstance(tracker,Tracker))