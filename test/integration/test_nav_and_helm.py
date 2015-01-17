from setup_test import setup_test
setup_test()

import unittest
from mock import Mock, call

import datetime
from fake_moving_gps import FakeMovingGPS


from navigator import Navigator
from helm import Helm
from waypoint import Waypoint
from position import Position
from globe import Globe
from config import CONFIG

def print_msg(msg):
    print msg

class TestNavigationAndHelm(unittest.TestCase):
    
    def setUp(self):
        self.logger = Mock()
        self.logger.error = Mock(side_effect=print_msg)
        self.servo = Mock()
    
    def test_should_steer_to_next_waypoint(self):
        destination = Waypoint(Position(10.03,10.03),10)
        gps = FakeMovingGPS([Position(10,10),Position(10.01,10.01),Position(10.02,10.02),Position(10.03,10.03)])
        helm = Helm(gps,self.servo,Mock(),self.logger, CONFIG['helm'])
        navigator = Navigator(gps,helm,Globe(),self.logger, CONFIG['navigator'])

        navigator.to(destination)

        self.logger.info.assert_has_calls(
            [call('Navigator, steering to +10.030000,+10.030000, bearing  44.6, distance 4681.8m'),
            call('Navigator, steering to +10.030000,+10.030000, bearing  44.6, distance 3121.2m'),
            call('Navigator, steering to +10.030000,+10.030000, bearing  44.6, distance 1560.6m'),
            call('Navigator, arrived at +10.030000,+10.030000')])

    def test_should_steer_to_next_waypoint_with_kink_in_route(self):
        gps = FakeMovingGPS([Position(10,10),Position(10.01,10.01),Position(10.025,10.015),Position(10.03,10.03)])
        helm = Helm(gps,self.servo,Mock(),self.logger, CONFIG['helm'])
        navigator = Navigator(gps,helm,Globe(),self.logger, CONFIG['navigator'])
        destination = Waypoint(Position(10.03,10.03),10)
        navigator.to(destination)
        self.logger.info.assert_has_calls(
            [call('Navigator, steering to +10.030000,+10.030000, bearing  44.6, distance 4681.8m'),
            call('Navigator, steering to +10.030000,+10.030000, bearing  44.6, distance 3121.2m'),
            call('Navigator, steering to +10.030000,+10.030000, bearing  71.3, distance 1734.0m'),
            call('Navigator, arrived at +10.030000,+10.030000')])

    def test_should_steer_repeatedly_during_navigation(self):
        destination = Waypoint(Position(10.0003,10.0003),10)
        gps = FakeMovingGPS([Position(10,10),Position(10.0001,10.00015),Position(10.00025,10.0002),Position(10.0003,10.0003)])
        helm = Helm(gps,self.servo,Mock(),self.logger, CONFIG['helm'])
        navigator = Navigator(gps,helm,Globe(),self.logger, CONFIG['navigator'])

        navigator.to(destination)

        self.logger.debug.assert_has_calls(
            [call('Helm, steering 44.6, tracking 55.9, rate of turn +55.9, rudder +0.0, new rudder +30.0'),
            call('Helm, steering 44.6, tracking 55.9, rate of turn +0.0, rudder +30.0, new rudder +30.0'),
            call('Helm, steering 44.6, tracking 55.9, rate of turn +0.0, rudder +30.0, new rudder +30.0'),
            call('Helm, steering 44.6, tracking 55.9, rate of turn +0.0, rudder +30.0, new rudder +30.0'),
            call('Helm, steering 44.6, tracking 55.9, rate of turn +0.0, rudder +30.0, new rudder +30.0'),
            call('Helm, steering 44.6, tracking 55.9, rate of turn +0.0, rudder +30.0, new rudder +30.0'),
            call('Helm, steering 44.6, tracking 55.9, rate of turn +0.0, rudder +30.0, new rudder +30.0')])

