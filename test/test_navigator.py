from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call

from navigator import Navigator
from globe import Globe
from position import Position
from waypoint import Waypoint

class TestNavigator(unittest.TestCase):
    
    def setUp(self):
        self.current_position = Position(53,-2,5,5)
        self.mock_gps = Mock(position=self.current_position)
        self.mock_helm = Mock()
        self.globe = Globe()
    
    def test_should_steer_from_current_position_to_next(self):
        new_waypoint = Waypoint(Position(11,11),0)
        bearing = self.globe.bearing(self.current_position,new_waypoint.position)
        navigator = Navigator(self.mock_gps,self.mock_helm,self.globe)

        navigator.to(new_waypoint,None,None)
    
        self.mock_helm.steer.assert_called_with(bearing,navigator.check_progress)
    
    def test_should_invoke_callback_if_new_position_has_been_reached(self):
        mock_callback_nav_complete = Mock()
        navigator = Navigator(self.mock_gps,Mock(),self.globe)

        navigator.to(Waypoint(self.current_position,0),mock_callback_nav_complete,'arrived!')

        mock_callback_nav_complete.assert_called_with('arrived!')
        
    def test_should_allow_a_tolerance_and_consider_errors_when_calculating_if_we_have_reached_waypoint(self):
        mock_callback_nav_complete = Mock()
        new_waypoint = Waypoint(Position(53.0001,-1.9999),10)
        navigator = Navigator(self.mock_gps,Mock(),self.globe)

        navigator.to(new_waypoint,mock_callback_nav_complete,'arrived!')

        mock_callback_nav_complete.assert_called_with('arrived!')

    def test_should_not_signal_arrival_if_outside_tolerance(self):
        mock_callback_nav_complete = Mock()
        new_waypoint = Waypoint(Position(53.0001,-1.9999),5)
        navigator = Navigator(self.mock_gps,Mock(),self.globe)

        navigator.to(new_waypoint,mock_callback_nav_complete,'arrived!')

        self.assertEqual(mock_callback_nav_complete.call_count,0,"expected no call to nav complete")

    def test_should_check_bearing_and_adjust_to_new_circumstances(self):
        new_waypoint = Waypoint(Position(11,11),0)
        bearing = self.globe.bearing(self.current_position,new_waypoint.position)
        navigator = Navigator(self.mock_gps,self.mock_helm,self.globe)

        navigator.to(new_waypoint,None,None)
        self.mock_helm.steer.assert_called_with(bearing,navigator.check_progress)
        
        new_position = Position(12,12)
        self.mock_gps.position = new_position
        new_bearing = self.globe.bearing(new_position,new_waypoint.position)

        navigator.check_progress()
        self.mock_helm.steer.assert_called_with(new_bearing,navigator.check_progress)

    def test_should_check_bearing_and_signal_arrival_if_finished(self):
        mock_callback_nav_complete = Mock()
        new_waypoint = Waypoint(Position(11,11),0)
        navigator = Navigator(self.mock_gps,self.mock_helm,self.globe)

        navigator.to(new_waypoint,mock_callback_nav_complete,'arrived!')
        self.assertEqual(mock_callback_nav_complete.call_count,0,"expected no call to nav complete yet")

        self.mock_gps.position = new_waypoint.position

        navigator.check_progress()
        mock_callback_nav_complete.assert_called_with('arrived!')
        
#    should_log_decisions_to_debug