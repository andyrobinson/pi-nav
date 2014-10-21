from setup_test import setup_test
setup_test()

import unittest
from mock import Mock, call
import datetime

from navigator import Navigator
from position import Position

class TestNavigate(unittest.TestCase):
    def test_should_navigate_from_current_position_to_next_with_logging(self):
        mock_point_navigator = Mock()
        mock_logger = Mock()
        new_position = Position(11,11)

        navigator = Navigator(mock_point_navigator, mock_logger)
        navigator.follow_route([new_position])

        mock_point_navigator.to.assert_called_with(new_position, navigator.follow_route,[])
        mock_logger.info.assert_called_with('Navigating to {:+f},{:+f}'.format(new_position.longitude, new_position.latitude))

    def test_should_finish_navigation_and_log_on_empty(self):
        mock_point_navigator = Mock()
        mock_logger = Mock()

        navigator = Navigator(mock_point_navigator, mock_logger)
        navigator.follow_route([])

        mock_logger.info.assert_called_with('Navigation complete')
        
        
        


