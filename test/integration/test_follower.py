from setup_test import setup_test
setup_test()

import unittest
from mock import Mock, call
import datetime
from fake_moving_gps import FakeMovingGPS


from follower import Follower
from position import Position
from navigator import Navigator
from waypoint import Waypoint
from globe import Globe
from config import CONFIG
from events import Exchange,Event,EventName
from stub_timer import StubTimer
from event_source import EventSource

def print_msg(msg):
    print msg

class TestFollower(unittest.TestCase):

    def setUp(self):
        self.mock_logger = Mock()
        self.mock_logger.error = Mock(side_effect=print_msg)
        self.exchange = Exchange(self.mock_logger)
        self.exchange.subscribe(EventName.navigate,self.temp_signal_arrived)
        self.timer = StubTimer()
        self.event_source = EventSource(self.exchange,self.timer,self.mock_logger)
        self.mock_helm = Mock()
    	gps = FakeMovingGPS([Position(10,10),Position(11,11),Position(12,12),Position(13,13)])
        self.navigator = Navigator(gps,self.mock_helm,Globe(),self.mock_logger, CONFIG['navigator'])

    def temp_signal_arrived(self,event):
        self.exchange.publish(Event(EventName.arrived))

    def test_should_navigate_along_list_of_waypoints_with_logging(self):
        waypoint1 = Waypoint(Position(11,11),10)
        waypoint2 = Waypoint(Position(13,13),10)
        follower = Follower(self.exchange,self.navigator,[waypoint1,waypoint2],self.mock_logger)

        self.event_source.start()

        self.mock_logger.info.assert_has_calls(
            [call('Follower, next waypoint +11.000000,+11.000000'),
            # Ignored until navigator is also using events, when we can remove the temp_signal_arrived
            # call('Navigator, steering to +11.000000,+11.000000, bearing  44.4, distance 155941.2m'),
            # call('Navigator, arrived at +11.000000,+11.000000'),
            call('Follower, next waypoint +13.000000,+13.000000'),
            # call('Navigator, steering to +13.000000,+13.000000, bearing  44.2, distance 155399.6m'),
            # call('Navigator, arrivedz at +13.000000,+13.000000'),
            call('Follower, all waypoints reached, navigation complete')])

    def ignore_should_steer_towards_waypoints(self):
        waypoint = Waypoint(Position(11,11),10)
        gps = FakeMovingGPS([Position(10,10),Position(11,11)])
        follower = Follower(self.exchange,self.navigator,[waypoint],self.mock_logger)

        self.event_source.start()

        self.mock_helm.steer_course.assert_has_calls([call(44.42621683500943,CONFIG['navigator']['max time to steer'])])
