from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call

from navigator import Navigator
from globe import Globe
from position import Position
from waypoint import Waypoint
from nan import NaN, isNaN

def last_called_args(mock):
    return mock.call_args[0]

class FakeMovingGPS():
    def __init__(self,positions):
        self.positions = positions
        
    def get_position(self):
        value = self.positions[0]
        if len(self.positions) > 1:
            self.positions = self.positions[1:]
        return value
        
    position = property(get_position)    
        
class TestNavigator(unittest.TestCase):
    
    def setUp(self):
        self.current_position = Position(53,-2,5,5)
        self.mock_gps = Mock(position=self.current_position)
        self.mock_helm = Mock()
        self.globe = Globe()
        self.mock_logger = Mock()

    def test_should_not_steer_and_log_arrival_if_arrived(self):
        navigator = Navigator(self.mock_gps,self.mock_helm,self.globe, self.mock_logger)

        navigator.to(Waypoint(self.current_position,0))

        self.assertEqual(self.mock_helm.call_count,0,"expected no call to steer if we have arrived")
        self.mock_logger.info.assert_called_with('Navigator, arrived at {:+f},{:+f}'.format(self.current_position.latitude,self.current_position.longitude))

    def test_should_allow_a_tolerance_and_consider_errors_when_calculating_if_we_have_reached_waypoint(self):
        waypoint = Waypoint(Position(53.0001,-1.9999),10)
        navigator = Navigator(self.mock_gps,Mock(),self.globe, self.mock_logger)

        navigator.to(waypoint)

        self.assertEqual(self.mock_helm.call_count,0,"expected no call to steer if we have arrived")
        self.mock_logger.info.assert_called_with('Navigator, arrived at {:+f},{:+f}'.format(waypoint.latitude,waypoint.longitude))

    def test_should_steer_from_current_position_to_next_and_log_until_point_is_reached(self):
        waypoint = Waypoint(Position(11,11),0)
        bearing = self.globe.bearing(self.current_position,waypoint.position)
        fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
        navigator = Navigator(fake_gps,self.mock_helm,self.globe, self.mock_logger)

        navigator.to(waypoint)

        self.mock_logger.info.assert_any_call('Navigator, steering to {:+f},{:+f}, bearing {:5.1f}, distance {:.1f}m'
            .format(11.0,11.0,bearing,self.globe.distance_between(self.current_position,waypoint.position)))
        self.mock_helm.steer.assert_called_with(bearing)

    def test_should_steer_to_waypoint_if_outside_tolerance(self):
        waypoint = Waypoint(Position(53.0001,-1.9999),5)
        bearing = self.globe.bearing(self.current_position,waypoint.position)
        fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
        navigator = Navigator(fake_gps,self.mock_helm,self.globe, self.mock_logger)

        navigator.to(waypoint)

        self.mock_helm.steer.assert_called_with(bearing)

    def test_at_intermediate_point_should_adjust_heading(self):
        waypoint = Waypoint(Position(11,11),0)
        intermediate_position = Position(12,12)
        fake_gps = FakeMovingGPS([self.current_position, intermediate_position, waypoint.position])
        bearing1 = self.globe.bearing(self.current_position,waypoint.position)
        bearing2 = self.globe.bearing(intermediate_position,waypoint.position)
        navigator = Navigator(fake_gps,self.mock_helm,self.globe, Mock())

        navigator.to(waypoint)
        
        self.mock_helm.steer.has_calls([call(bearing1),call(bearing2)])
        
    def test_should_not_call_steer_with_NaN_bearing_even_if_GPS_lost_signal(self):
        waypoint = Waypoint(Position(-60,22),0)
        no_position = Position(NaN,NaN,NaN,NaN)
        fake_gps = FakeMovingGPS([self.current_position, no_position, waypoint.position])
        bearing = self.globe.bearing(self.current_position,waypoint.position)
        navigator = Navigator(fake_gps,self.mock_helm,self.globe, Mock())

        navigator.to(waypoint)

        self.assertFalse(isNaN(last_called_args(self.mock_helm.steer)[0]),'Steer called with NaN')
