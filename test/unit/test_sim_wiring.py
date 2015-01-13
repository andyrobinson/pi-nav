from setup_test import setup_test 
setup_test()

import unittest
import logging

from sim_wiring import SimWiring
from globe import Globe
from sensors import Sensors
from navigator import Navigator
from helm import Helm

class TestSimWiring(unittest.TestCase):

    def setUp(self):
        self.wiring = SimWiring()
        
    def test_should_return_singleton_globe(self):
        globe = self.wiring.globe
        self.assertEqual(globe, self.wiring.globe)
        self.assertTrue(isinstance(globe, Globe))

    def test_should_return_singleton_console_logger(self):
        logger = self.wiring.console_logger
        self.assertEqual(logger, self.wiring.console_logger)
        self.assertTrue(isinstance(logger, logging.Logger))

    def test_navigator_simulator_should_use_sensors(self):
        navigator = self.wiring.navigator_simulator
        self.assertTrue(isinstance(navigator.sensors,Sensors))

    def test_navigator_should_use_real_heml(self):
        navigator = self.wiring.navigator_simulator
        self.assertTrue(isinstance(navigator.helm,Helm))

    def test_follower_simulator_should_use_navigator(self):
        follower = self.wiring.follower_simulator
        self.assertTrue(isinstance(follower.navigator,Navigator))

    def test_helm_should_use_fake_servo_and_timer(self):
        helm = self.wiring.helm
        vehicle = self.wiring.vehicle
        self.assertEqual(helm.rudder_servo,vehicle.rudder)
        self.assertEqual(helm.timer,vehicle.timer)