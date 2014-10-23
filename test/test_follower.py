from setup_test import setup_test
setup_test()

import unittest
from mock import Mock, call
import datetime

from follower import Follower
from position import Position

class TestFollower(unittest.TestCase):
    def test_should_navigate_along_list_of_waypoints_with_logging(self):
        mock_navigator = Mock()
        mock_logger = Mock()
        position1 = Position(11,11)
        position2 = Position(12,12)

        navigator = Follower(mock_navigator, mock_logger)
        navigator.follow_route([position1,position2])

        mock_navigator.to.has_calls([call(position1),call(position2)])
        mock_logger.info.has_calls(
            [call('Follower, next waypoint {:+f},{:+f}'.format(position1.longitude, position1.latitude)),
             call('Follower, next waypoint {:+f},{:+f}'.format(position2.longitude, position2.latitude)),
             call('Follower, all waypoints reached, navigation complete')])

    def test_should_finish_navigation_and_log_on_empty(self):
        mock_navigator = Mock()
        mock_logger = Mock()

        navigator = Follower(mock_navigator, mock_logger)
        navigator.follow_route([])

        mock_logger.info.assert_called_with('Follower, all waypoints reached, navigation complete')


