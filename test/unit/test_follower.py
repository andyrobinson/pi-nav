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
        self.follower = Follower(self.exchange,self.mock_navigator, self.mock_logger)

    def event_recorder(self,event):
        self.last_event = event

    def listen(self,event_name):
        self.exchange.subscribe(event_name,self.event_recorder)

    def test_should_signal_a_navigate_event_using_the_first_waypoint(self):
        self.listen("navigate")

        firstwaypoint = Waypoint(Position(1,1),5)

        self.follower.follow([firstwaypoint])
        self.assertEqual(self.last_event.name,"navigate")
        self.assertEqual(self.last_event.waypoint,firstwaypoint)

    def test_should_navigate_to_the_next_waypoint_when_a_waypoint_is_reached(self):
        self.listen("navigate")

        waypoint1 = Waypoint(Position(1,1),5)
        waypoint2 = Waypoint(Position(2,2),5)
        self.follower.follow([waypoint1,waypoint2])
        self.exchange.publish(Event("arrived",waypoint1))

        self.assertEqual(self.last_event.waypoint,waypoint2)

    def test_should_navigate_along_list_of_waypoints_with_logging(self):
        waypoint1 = Waypoint(Position(1,1),5)
        waypoint2 = Waypoint(Position(2,2),5)

        self.follower.follow([waypoint1,waypoint2])

        self.exchange.publish(Event("arrived",waypoint1))
        self.exchange.publish(Event("arrived",waypoint2))

        self.mock_logger.info.assert_has_calls(
            [call('Follower, next waypoint {:+f},{:+f}'.format(waypoint1.longitude, waypoint1.latitude)),
             call('Follower, next waypoint {:+f},{:+f}'.format(waypoint2.longitude, waypoint2.latitude)),
             call('Follower, all waypoints reached, navigation complete')])

#  Interestingly errors are no longer handled at this level.  We need something that
#  Feeds the (timer based) event stream higher up, and can catch all errors
#  Maybe we add this to the follow method; not sure

    # def test_errors_should_be_logged_and_navigation_continues(self):
    #     position1 = Position(11,11)
    #     position2 = Position(12,12)
    #
    #     TestFollower.raise_error = True
    #
    #     def fail_first_time(self):
    #         if TestFollower.raise_error:
    #             TestFollower.raise_error = False
    #             raise RuntimeError('oops')
    #
    #     mock_nav = Mock()
    #     mock_nav.configure_mock(**{'to.side_effect': fail_first_time})
    #
    #     follower = Follower(mock_nav, self.mock_logger)
    #
    #     follower.follow_route([position1,position2])
    #     mock_nav.to.assert_has_calls([call(position1),call(position2)])
    #     self.mock_logger.error.assert_called_with('Follower, RuntimeError: oops')
    #
    # def test_errors_during_error_logging_should_be_skipped_and_navigation_continues(self):
    #     position1 = Position(11,11)
    #     position2 = Position(12,12)
    #
    #     TestFollower.raise_error = True
    #
    #     def fail_first_time(self):
    #         if TestFollower.raise_error:
    #             TestFollower.raise_error = False
    #             raise RuntimeError('oops')
    #
    #     mock_nav = Mock()
    #     mock_nav.configure_mock(**{'to.side_effect': fail_first_time})
    #
    #     mock_logger = Mock()
    #     mock_logger.configure_mock(**{'error.side_effect': RuntimeError})
    #
    #     follower = Follower(mock_nav, mock_logger)
    #
    #     follower.follow_route([position1,position2])
    #     mock_nav.to.assert_has_calls([call(position1),call(position2)])
