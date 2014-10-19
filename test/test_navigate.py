from setup_test import setup_test
setup_test()

import unittest
from mock import Mock, call
import datetime

from navigator import Navigator
from position import Position

class TestNavigate(unittest.TestCase):
    def test_should_navigate_from_current_position_to_next(self):
        mock_point_navigator = Mock()
        new_position = Position(11,11)

        navigator = Navigator(mock_point_navigator)
        navigator.follow_route([new_position])

        mock_point_navigator.to.assert_called_with(new_position, navigator.follow_route,[])
        
        
        


