from setup_test import setup_test
setup_test()

import unittest
from mock import Mock, call
import datetime

from follower import Follower
from position import Position
from events import Exchange, Event
from waypoint import Waypoint

class TestFollower(unittest.TestCase):

    def setUp(self):
        self.mock_navigator = Mock()
        self.mock_logger = Mock()
        self.exchange = Exchange(self.mock_logger)
        self.last_event = Event("no event fired")

    def event_recorder(self,event):
        self.last_event = event

    def listen(self,event_name):
        self.exchange.subscribe(event_name,self.event_recorder)

    def test_should_signal_a_navigate_event_using_the_first_waypoint(self):
        self.listen(Event.navigate)
        firstwaypoint = Waypoint(Position(1,1),5)
        follower = Follower(self.exchange,self.mock_navigator, [firstwaypoint],self.mock_logger)

        self.exchange.publish(Event(Event.start))
        self.assertEqual(self.last_event.name,Event.navigate)
        self.assertEqual(self.last_event.waypoint,firstwaypoint)

    def test_should_navigate_to_the_next_waypoint_when_a_waypoint_is_reached(self):
        self.listen(Event.navigate)
        waypoint1 = Waypoint(Position(1,1),5)
        waypoint2 = Waypoint(Position(2,2),5)
        follower = Follower(self.exchange,self.mock_navigator, [waypoint1,waypoint2],self.mock_logger)

        self.exchange.publish(Event(Event.start))
        self.exchange.publish(Event(Event.arrived,waypoint1))

        self.assertEqual(self.last_event.waypoint,waypoint2)

    def test_should_signal_end_when_all_waypoints_exhausted(self):
        self.listen(Event.end)
        follower = Follower(self.exchange,self.mock_navigator, [],self.mock_logger)

        self.exchange.publish(Event(Event.start))
        self.assertEqual(self.last_event.name,Event.end)

    def test_should_navigate_along_list_of_waypoints_with_logging(self):
        waypoint1 = Waypoint(Position(1,1),5)
        waypoint2 = Waypoint(Position(2,2),5)

        follower = Follower(self.exchange,self.mock_navigator, [waypoint1,waypoint2],self.mock_logger)

        self.exchange.publish(Event(Event.start))
        self.exchange.publish(Event(Event.arrived,waypoint1))
        self.exchange.publish(Event(Event.arrived,waypoint2))

        self.mock_logger.info.assert_has_calls(
            [call('Follower, next waypoint {:+f},{:+f}'.format(waypoint1.longitude, waypoint1.latitude)),
             call('Follower, next waypoint {:+f},{:+f}'.format(waypoint2.longitude, waypoint2.latitude)),
             call('Follower, all waypoints reached, navigation complete')])
