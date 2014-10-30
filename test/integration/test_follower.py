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

def print_msg(msg):
    print msg

class TestFollower(unittest.TestCase):
    
    def setUp(self):
        self.mock_logger = Mock()
        self.mock_logger.error = Mock(side_effect=print_msg)
        self.mock_helm = Mock()
	gps = FakeMovingGPS([Position(10,10),Position(11,11),Position(12,12),Position(13,13)])
        navigator = Navigator(gps,self.mock_helm,Globe(),self.mock_logger)
        self.follower = Follower(navigator, self.mock_logger)
    
    def test_should_navigate_along_list_of_waypoints_with_logging(self):
        waypoint1 = Waypoint(Position(11,11),10)
        waypoint2 = Waypoint(Position(13,13),10)

        self.follower.follow_route([waypoint1,waypoint2])

        self.mock_logger.info.has_calls(
            [call('Follower, next waypoint {:+f},{:+f}'.format(waypoint1.position.longitude, waypoint1.position.latitude)),
             call('Follower, next waypoint {:+f},{:+f}'.format(waypoint2.position.longitude, waypoint2.position.latitude)),
             call('Follower, all waypoints reached, navigation complete')])


