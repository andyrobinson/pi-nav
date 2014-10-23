from setup_test import setup_test
setup_test()

import unittest
from mock import Mock, call
import datetime

from follower import Follower
from position import Position

class TestFollower(unittest.TestCase):
    def test_should_navigate_from_current_position_to_next_with_logging(self):
        mock_navigator = Mock()
        mock_logger = Mock()
        new_position = Position(11,11)

        navigator = Follower(mock_navigator, mock_logger)
        navigator.follow_route([new_position])

        mock_navigator.to.assert_called_with(new_position, navigator.follow_route,[])
        mock_logger.info.assert_called_with('Follower, next waypoint {:+f},{:+f}'.format(new_position.longitude, new_position.latitude))

    def test_should_finish_navigation_and_log_on_empty(self):
        mock_navigator = Mock()
        mock_logger = Mock()

        navigator = Follower(mock_navigator, mock_logger)
        navigator.follow_route([])

        mock_logger.info.assert_called_with('Follower, all waypoints reached, navigation complete')
        
        
        


