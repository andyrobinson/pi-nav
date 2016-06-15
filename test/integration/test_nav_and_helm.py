from setup_test import setup_test
setup_test()

import logging
import unittest
from mock import Mock, call

from bearing import angle_between,to_360
from fake_moving_gps import FakeMovingGPS
from fake_sensors import FakeSensors
from navigator import Navigator
from helm import Helm
from steerer import Steerer
from course_steerer import CourseSteerer
from waypoint import Waypoint
from position import Position
from globe import Globe
from config import CONFIG
from events import Event,Exchange,EventName
from stub_timer import StubTimer
from timeshift import TimeShift
from sensors import Sensors
from test_utils import test_logger

def print_msg(msg):
    print msg

class TestNavigationAndHelm(unittest.TestCase):

    def ticks(self,number,duration):
        for i in range(1,number):
            self.exchange.publish(Event(EventName.tick))
            self.timer.wait_for(duration)

    def setUp(self):
        self.logger = Mock()
        self.logger.error = Mock(side_effect=print_msg)
        self.servo = Mock()

        self.exchange = Exchange(self.logger)
        self.timer = StubTimer()
        TimeShift(self.exchange,self.timer.time)

    def test_should_steer_to_next_waypoint(self):
        destination = Waypoint(Position(10.03,10.03),10)
        gps = FakeMovingGPS([Position(10,10),Position(10.01,10.01),Position(10.02,10.02),Position(10.03,10.03)])
        sensors = FakeSensors(gps,1,45)
        steerer = Steerer(self.servo,self.logger, CONFIG['steerer'])
        helm = Helm(self.exchange,sensors,steerer,self.logger, CONFIG['helm'])
        navigator = Navigator(sensors,Globe(),self.exchange,self.logger, CONFIG['navigator'])

        self.exchange.publish(Event(EventName.navigate,waypoint = destination))
        self.ticks(number = 14,duration=200)

        self.logger.info.assert_has_calls(
            [call('Navigator, steering to +10.030000,+10.030000, bearing  44.6, distance 4681.8m'),
            call('Navigator, steering to +10.030000,+10.030000, bearing  44.6, distance 3121.2m'),
            call('Navigator, steering to +10.030000,+10.030000, bearing  44.6, distance 1560.6m'),
            call('Navigator, arrived at +10.030000,+10.030000')])

    def test_should_steer_to_next_waypoint_with_kink_in_route(self):
        destination = Waypoint(Position(10.03,10.03),10)
        gps = FakeMovingGPS([Position(10,10),Position(10.01,10.01),Position(10.025,10.015),Position(10.03,10.03)])
        sensors = FakeSensors(gps,1,45)
        steerer = Steerer(self.servo,self.logger, CONFIG['steerer'])
        helm = Helm(self.exchange,sensors,steerer,self.logger, CONFIG['helm'])
        navigator = Navigator(sensors,Globe(),self.exchange,self.logger, CONFIG['navigator'])

        self.exchange.publish(Event(EventName.navigate,waypoint = destination))
        self.ticks(number = 14,duration=200)

        self.logger.info.assert_has_calls(
            [call('Navigator, steering to +10.030000,+10.030000, bearing  44.6, distance 4681.8m'),
            call('Navigator, steering to +10.030000,+10.030000, bearing  44.6, distance 3121.2m'),
            call('Navigator, steering to +10.030000,+10.030000, bearing  71.3, distance 1734.0m'),
            call('Navigator, arrived at +10.030000,+10.030000')])

    def test_should_steer_repeatedly_during_navigation(self):
        logger = Mock()
        destination = Waypoint(Position(10.0003,10.0003),10)
        gps = FakeMovingGPS([Position(10,10),Position(10.0001,10.00015),Position(10.00025,10.0002),Position(10.0003,10.0003)])
        sensors = FakeSensors(gps,1,45)
        steerer = Steerer(self.servo,logger, CONFIG['steerer'])
        helm = Helm(self.exchange,sensors,steerer,logger, CONFIG['helm'])
        navigator = Navigator(sensors,Globe(),self.exchange,self.logger, CONFIG['navigator'])

        self.exchange.publish(Event(EventName.navigate,waypoint = destination))
        self.ticks(number = 10,duration=20)

        logger.debug.assert_has_calls(
            [call('Helm, steering 36.4, heading 45.0, rate of turn +1.0, rudder +0.0, new rudder +9.6'),
             call('Helm, steering 36.4, heading 45.0, rate of turn +1.0, rudder +9.6, new rudder +19.1'),
             call('Helm, steering 36.4, heading 45.0, rate of turn +1.0, rudder +19.1, new rudder +28.7'),
             call('Helm, steering 63.1, heading 45.0, rate of turn +1.0, rudder +28.7, new rudder +11.6'),
             call('Helm, steering 63.1, heading 45.0, rate of turn +1.0, rudder +11.6, new rudder -5.5'),
             call('Helm, steering 63.1, heading 45.0, rate of turn +1.0, rudder -5.5, new rudder -22.6'),
             call('Helm, steering 63.1, heading 45.0, rate of turn +1.0, rudder -22.6, new rudder -30.0'),
             call('Helm, steering 63.1, heading 45.0, rate of turn +1.0, rudder -30.0, new rudder -30.0'),
             call('Helm, steering 63.1, heading 45.0, rate of turn +1.0, rudder -30.0, new rudder -30.0'),
             call('Helm, steering 63.1, heading 45.0, rate of turn +1.0, rudder -30.0, new rudder -30.0'),
             call('Helm, steering 63.1, heading 45.0, rate of turn +1.0, rudder -30.0, new rudder -30.0'),
             call('Helm, steering 63.1, heading 45.0, rate of turn +1.0, rudder -30.0, new rudder -30.0'),
             call('Helm, steering 63.1, heading 45.0, rate of turn +1.0, rudder -30.0, new rudder -30.0'),
             call('Helm, steering 63.1, heading 45.0, rate of turn +1.0, rudder -30.0, new rudder -30.0')])

if __name__ == "__main__":
    unittest.main()
