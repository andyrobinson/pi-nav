from setup_test import setup_test
setup_test()

import unittest
from mock import Mock, call
import datetime

from follower import Follower
from position import Position

class TestFollower(unittest.TestCase):
    
    def setUp(self):
        self.mock_navigator = Mock()
        self.mock_logger = Mock()
        self.follower = Follower(self.mock_navigator, self.mock_logger)
    
    def test_should_navigate_along_list_of_waypoints_with_logging(self):
        position1 = Position(11,11)
        position2 = Position(12,12)

        self.follower.follow_route([position1,position2])

        self.mock_navigator.to.assert_has_calls([call(position1),call(position2)])
        self.mock_logger.info.assert_has_calls(
            [call('Follower, next waypoint {:+f},{:+f}'.format(position1.longitude, position1.latitude)),
             call('Follower, next waypoint {:+f},{:+f}'.format(position2.longitude, position2.latitude)),
             call('Follower, all waypoints reached, navigation complete')])

    def test_should_finish_navigation_and_log_on_empty(self):
        self.follower.follow_route([])

        self.mock_logger.info.assert_called_with('Follower, all waypoints reached, navigation complete')

    def test_should_raise_an_error_from_a_mock(self):
        mock = Mock(**{'throw.side_effect': KeyError})
        self.assertRaises(KeyError, mock.throw)

    def test_errors_should_be_logged_and_navigation_continues(self):
        position1 = Position(11,11)
        position2 = Position(12,12)

        TestFollower.raise_error = True

        def fail_first_time(self):
            if TestFollower.raise_error:
                TestFollower.raise_error = False
                raise RuntimeError('oops')

        mock_nav = Mock()
        mock_nav.configure_mock(**{'to.side_effect': fail_first_time})

        follower = Follower(mock_nav, self.mock_logger)

        follower.follow_route([position1,position2])
        mock_nav.to.assert_has_calls([call(position1),call(position2)])
        self.mock_logger.error.assert_called_with('Follower, RuntimeError: oops')

    def test_errors_during_error_logging_should_be_skipped_and_navigation_continues(self):
        position1 = Position(11,11)
        position2 = Position(12,12)

        TestFollower.raise_error = True

        def fail_first_time(self):
            if TestFollower.raise_error:
                TestFollower.raise_error = False
                raise RuntimeError('oops')

        mock_nav = Mock()
        mock_nav.configure_mock(**{'to.side_effect': fail_first_time})

        mock_logger = Mock()
        mock_logger.configure_mock(**{'error.side_effect': RuntimeError})

        follower = Follower(mock_nav, mock_logger)

        follower.follow_route([position1,position2])
        mock_nav.to.assert_has_calls([call(position1),call(position2)])
