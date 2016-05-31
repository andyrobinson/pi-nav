from setup_test import setup_test
setup_test()

import unittest
from mock import Mock, call
import datetime

from follower import Follower
from position import Position
from events import Exchange, Event, EventName
from waypoint import Waypoint
from test_utils import EventTestCase


class TestFollower(EventTestCase):

    def setUp(self):
        super(TestFollower, self).setUp()
        self.mock_logger = Mock()

    def test_should_signal_a_navigate_event_using_the_first_waypoint(self):
        self.listen(EventName.navigate)
        firstwaypoint = Waypoint(Position(1,1),5)
        follower = Follower(self.exchange,[firstwaypoint],self.mock_logger)

        self.exchange.publish(Event(EventName.start))
        self.assertEqual(self.last_event.name,EventName.navigate)
        self.assertEqual(self.last_event.waypoint,firstwaypoint)

    def test_should_navigate_to_the_next_waypoint_when_a_waypoint_is_reached(self):
        self.listen(EventName.navigate)
        waypoint1 = Waypoint(Position(1,1),5)
        waypoint2 = Waypoint(Position(2,2),5)
        follower = Follower(self.exchange,[waypoint1,waypoint2],self.mock_logger)

        self.exchange.publish(Event(EventName.start))
        self.exchange.publish(Event(EventName.arrived,waypoint1))

        self.assertEqual(self.last_event.waypoint,waypoint2)

    def test_should_signal_end_when_all_waypoints_exhausted(self):
        self.listen(EventName.end)
        follower = Follower(self.exchange,[],self.mock_logger)

        self.exchange.publish(Event(EventName.start))
        self.assertEqual(self.last_event.name,EventName.end)

    def test_should_navigate_along_list_of_waypoints_with_logging(self):
        waypoint1 = Waypoint(Position(1,1),5)
        waypoint2 = Waypoint(Position(2,2),5)

        follower = Follower(self.exchange,[waypoint1,waypoint2],self.mock_logger)

        self.exchange.publish(Event(EventName.start))
        self.exchange.publish(Event(EventName.arrived,waypoint1))
        self.exchange.publish(Event(EventName.arrived,waypoint2))

        self.mock_logger.info.assert_has_calls(
            [call('Follower, next waypoint {:+f},{:+f}'.format(waypoint1.longitude, waypoint1.latitude)),
             call('Follower, next waypoint {:+f},{:+f}'.format(waypoint2.longitude, waypoint2.latitude)),
             call('Follower, all waypoints reached, navigation complete')])
