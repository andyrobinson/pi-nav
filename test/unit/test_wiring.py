from setup_test import setup_test
setup_test()

import unittest
import logging

from wiring import Wiring,RUDDER_SERVO_CHANNEL
from globe import Globe
from sensors import Sensors
from navigator import Navigator
from follower import Follower
from simulate.stub_gps import StubGPS
from config import CONFIG
from helm import Helm

class TestWiring(unittest.TestCase):

    def setUp(self):
        self.wiring = Wiring(StubGPS(),None)

    def test_should_return_stub_gps_for_test_purposes(self):
        gps = self.wiring.gps
        self.assertTrue(isinstance(gps,StubGPS))

    def test_should_return_singleton_globe(self):
        globe = self.wiring.globe
        self.assertEqual(globe, self.wiring.globe)
        self.assertTrue(isinstance(globe, Globe))

    def test_should_return_singleton_application_logger(self):
        logger = self.wiring.application_logger
        self.assertEqual(logger, self.wiring.application_logger)
        self.assertTrue(isinstance(logger, logging.Logger))

    def test_should_return_sensors_with_gps(self):
        sensors = self.wiring.sensors
        self.assertTrue(isinstance(sensors,Sensors))
        self.assertEqual(sensors.gps,self.wiring.gps)

    def test_should_return_rudder_servo_with_30_degree_movement(self):
        rudder_servo = self.wiring.rudder_servo
        self.assertEqual(rudder_servo.channel,0)
        self.assertEqual(rudder_servo.channel,RUDDER_SERVO_CHANNEL)
        self.assertEqual(rudder_servo.min_pulse,1160)
        self.assertEqual(rudder_servo.min_angle,-30)
        self.assertEqual(rudder_servo.total_arc,60)
        self.assertEqual(rudder_servo.pulse_range,340*2)

    def test_should_return_helm_with_all_dependencies(self):
        helm = self.wiring.helm
        self.assertTrue(isinstance(helm,Helm))
        self.assertEqual(helm.full_deflection,CONFIG['helm']['full deflection'])
        self.assertEqual(helm.logger,self.wiring.application_logger)
        self.assertEqual(helm.sensors,self.wiring.sensors)
        self.assertEqual(helm.rudder_servo,self.wiring.rudder_servo)

    def test_should_return_navigator(self):
        navigator = self.wiring.navigator
        self.assertTrue(isinstance(navigator, Navigator))
        self.assertEqual(navigator.course_steerer,self.wiring.course_steerer)

    def test_should_use_corrct_config_in_navigator(self):
        navigator = self.wiring.navigator
        self.assertEqual(navigator.config,CONFIG['navigator'])
