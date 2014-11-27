from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call
from fake_moving_gps import FakeMovingGPS

from navigator import Navigator
from globe import Globe
from position import Position
from waypoint import Waypoint
from nan import NaN, isNaN

MIN_TIME_TO_STEER = 7
MAX_TIME_TO_STEER = 200000

def last_called_args(mock):
    return mock.call_args[0]

def expected_steering_duration(position, destination, speed):
    globe = Globe()
    distance = globe.distance_between(position, destination)
    return int(distance /speed)

class TestNavigator(unittest.TestCase):
    
    def setUp(self):
        self.current_position = Position(53,-2,5,5)
        self.mock_gps = Mock(position=self.current_position)
        self.mock_helm = Mock()
        self.globe = Globe()
        self.mock_logger = Mock()
        self.config = {'min time to steer' : MIN_TIME_TO_STEER, 'max time to steer' : MAX_TIME_TO_STEER}

    def test_should_not_steer_and_log_arrival_if_arrived(self):
        navigator = Navigator(self.mock_gps,self.mock_helm,self.globe, self.mock_logger, self.config)

        navigator.to(Waypoint(self.current_position,0))

        self.assertEqual(self.mock_helm.call_count,0,"expected no call to steer course if we have arrived")
        self.mock_logger.info.assert_called_with('Navigator, arrived at {:+f},{:+f}'.format(self.current_position.latitude,self.current_position.longitude))

    def test_should_allow_a_tolerance_and_consider_errors_when_calculating_if_we_have_reached_waypoint(self):
        waypoint = Waypoint(Position(53.0001,-1.9999),10)
        navigator = Navigator(self.mock_gps,Mock(),self.globe, self.mock_logger, self.config)

        navigator.to(waypoint)

        self.assertEqual(self.mock_helm.call_count,0,"expected no call to steer course if we have arrived")
        self.mock_logger.info.assert_called_with('Navigator, arrived at {:+f},{:+f}'.format(waypoint.latitude,waypoint.longitude))

    def test_should_steer_from_current_position_to_next_and_log_until_point_is_reached(self):
        waypoint = Waypoint(Position(53.5,-1.5),0)
        fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
        navigator = Navigator(fake_gps,self.mock_helm,self.globe, self.mock_logger, self.config)
        expected_bearing = self.globe.bearing(self.current_position,waypoint.position)
        expected_time = expected_steering_duration(self.current_position,waypoint.position,fake_gps.speed)

        navigator.to(waypoint)

        self.mock_logger.info.assert_any_call('Navigator, steering to {:+f},{:+f}, bearing {:5.1f}, distance {:.1f}m'
            .format(waypoint.latitude,waypoint.longitude,expected_bearing,self.globe.distance_between(self.current_position,waypoint.position)))
        self.mock_helm.steer_course.assert_called_with(expected_bearing, expected_time)

    def test_should_steer_to_waypoint_if_outside_tolerance(self):
        waypoint = Waypoint(Position(53.0001,-1.9999),5)
        fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
        navigator = Navigator(fake_gps,self.mock_helm,self.globe, self.mock_logger, self.config)
        expected_bearing = self.globe.bearing(self.current_position,waypoint.position)
        expected_time = expected_steering_duration(self.current_position,waypoint.position,fake_gps.speed)

        navigator.to(waypoint)

        self.mock_helm.steer_course.assert_called_with(expected_bearing,expected_time)

    def test_at_intermediate_point_should_adjust_heading(self):
        waypoint = Waypoint(Position(11,11),0)
        intermediate_position = Position(12,12)
        fake_gps = FakeMovingGPS([self.current_position, intermediate_position, waypoint.position])
        bearing1 = self.globe.bearing(self.current_position,waypoint.position)
        bearing2 = self.globe.bearing(intermediate_position,waypoint.position)
        time2 = expected_steering_duration(intermediate_position, waypoint.position,fake_gps.speed)
        navigator = Navigator(fake_gps,self.mock_helm,self.globe, Mock(), self.config)

        navigator.to(waypoint)
        
        self.mock_helm.steer_course.assert_has_calls([call(bearing1,MAX_TIME_TO_STEER),call(bearing2,time2)])
        
    def test_should_not_call_steer_with_NaN_bearing_even_if_GPS_lost_signal(self):
        waypoint = Waypoint(Position(-60,22),0)
        no_position = Position(NaN,NaN,NaN,NaN)
        fake_gps = FakeMovingGPS([self.current_position, no_position, waypoint.position])
        bearing = self.globe.bearing(self.current_position,waypoint.position)
        navigator = Navigator(fake_gps,self.mock_helm,self.globe, Mock(), self.config)

        navigator.to(waypoint)

        self.assertFalse(isNaN(last_called_args(self.mock_helm.steer_course)[0]),'Steer called with NaN')

    def test_should_ask_helm_to_steer_course_to_way_point_based_on_speed(self):
        waypoint = Waypoint(Position(53.0001,-1.999699),5) #23m from current position
        bearing = self.globe.bearing(self.current_position,waypoint.position)
        fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
        navigator = Navigator(fake_gps,self.mock_helm,self.globe, self.mock_logger, self.config)
        for_expected_seconds = expected_steering_duration(self.current_position,waypoint.position,fake_gps.speed)

        navigator.to(waypoint)

        self.mock_helm.steer_course.assert_called_with(bearing,for_expected_seconds)

    def test_should_return_minimum_steer_time_if_time_calculation_results_in_NaN(self):
        waypoint = Waypoint(Position(-60,22),0)
        no_position = Position(NaN,NaN,NaN,NaN)
        fake_gps = FakeMovingGPS([self.current_position, no_position, waypoint.position])
        expected_bearing = self.globe.bearing(self.current_position,waypoint.position)

        navigator = Navigator(fake_gps,self.mock_helm,self.globe, Mock(), self.config)
        navigator.to(waypoint)

        self.mock_helm.steer_course.assert_has_calls([
            call(expected_bearing,MAX_TIME_TO_STEER),
            call(expected_bearing,MIN_TIME_TO_STEER)])

    def test_should_use_minimum_steer_time_if_time_calculation_returns_small_value(self):
        waypoint = Waypoint(Position(53.0001,-1.9999),5)
        fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
        fake_gps.speed = 100
        expected_bearing = self.globe.bearing(self.current_position,waypoint.position)
        expected_time = expected_steering_duration(self.current_position,waypoint.position,fake_gps.speed)

        navigator = Navigator(fake_gps,self.mock_helm,self.globe, self.mock_logger, self.config)
        navigator.to(waypoint)

        self.mock_helm.steer_course.assert_called_with(expected_bearing,MIN_TIME_TO_STEER)

    def test_should_use_maximum_steer_time_if_its_a_long_way_to_go(self):
        waypoint = Waypoint(Position(60.0001,10),5)
        fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
        fake_gps.speed = 1
        expected_bearing = self.globe.bearing(self.current_position,waypoint.position)
        expected_time = expected_steering_duration(self.current_position,waypoint.position,fake_gps.speed)

        navigator = Navigator(fake_gps,self.mock_helm,self.globe, self.mock_logger, self.config)
        navigator.to(waypoint)

        self.mock_helm.steer_course.assert_called_with(expected_bearing,MAX_TIME_TO_STEER)

    def test_should_use_a_minimum_speed_for_calculation_preventing_divide_by_zero_error(self):
        waypoint = Waypoint(Position(53.001,-2.001),5)
        fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
        fake_gps.speed = 0
        expected_bearing = self.globe.bearing(self.current_position,waypoint.position)
        expected_time = expected_steering_duration(self.current_position,waypoint.position,0.01)

        navigator = Navigator(fake_gps,self.mock_helm,self.globe, self.mock_logger, self.config)
        navigator.to(waypoint)

        self.mock_helm.steer_course.assert_called_with(expected_bearing,expected_time)

