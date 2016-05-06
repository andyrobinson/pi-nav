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
from events import Exchange, Event,EventName

MIN_TIME_TO_STEER = 7
MAX_TIME_TO_STEER = 200000

def last_called_args(mock):
    return mock.call_args[0]

def time_to_destination(position, destination, speed):
    globe = Globe()
    distance = globe.distance_between(position, destination)
    return distance /speed

def expected_time_to_steer(position, destination, speed):
    return int(0.75 * time_to_destination(position, destination, speed))

class TestNavigator(unittest.TestCase):

    def event_recorder(self,event):
        self.last_listened_event = event
        self.event_count[event.name] = self.event_count[event.name] + 1

    def listen(self,event_name):
        self.event_count[event_name] = 0
        self.exchange.subscribe(event_name,self.event_recorder)

    def setUp(self):
        self.event_count = {}
        self.current_position = Position(53,-2,5,5)
        self.mock_gps = Mock(position=self.current_position)
        self.mock_helm = Mock()
        self.globe = Globe()
        self.mock_logger = Mock()
        self.config = {'min time to steer' : MIN_TIME_TO_STEER, 'max time to steer' : MAX_TIME_TO_STEER}
        self.exchange = Exchange(self.mock_logger)

    def test_should_not_steer_and_log_arrival_if_arrived(self):
        self.listen(EventName.arrived)
        self.listen(EventName.steer)
        navigator = Navigator(self.mock_gps,self.mock_helm,self.globe, self.exchange, self.mock_logger, self.config)

        self.exchange.publish(Event(EventName.navigate,Waypoint(self.current_position,0)))

        self.assertEqual(self.event_count[EventName.steer],0,"expected no event to steer course if we have arrived")
        self.assertEqual(self.event_count[EventName.arrived],1,"expected arrived event if we have arrived")
        self.mock_logger.info.assert_called_with('Navigator, arrived at {:+f},{:+f}'.format(self.current_position.latitude,self.current_position.longitude))

    def test_should_allow_a_tolerance_and_consider_errors_when_calculating_if_we_have_reached_waypoint(self):
        self.listen(EventName.arrived)
        self.listen(EventName.steer)
        waypoint = Waypoint(Position(53.0001,-1.9999),10)
        navigator = Navigator(self.mock_gps,self.mock_helm,self.globe, self.exchange, self.mock_logger, self.config)

        self.exchange.publish(Event(EventName.navigate,waypoint))

        self.assertEqual(self.event_count[EventName.arrived],1,"expected arrived event if we have arrived")
        self.mock_logger.info.assert_called_with('Navigator, arrived at {:+f},{:+f}'.format(waypoint.latitude,waypoint.longitude))

    def test_should_steer_along_the_bearing_to_the_next_waypoint(self):
        self.listen(EventName.steer)
        waypoint = Waypoint(Position(53.5,-1.5),0)
        expected_distance = self.globe.distance_between(self.current_position,waypoint.position)
        expected_bearing = self.globe.bearing(self.current_position,waypoint.position)

        navigator = Navigator(self.mock_gps,self.mock_helm,self.globe, self.exchange, self.mock_logger, self.config)

        self.exchange.publish(Event(EventName.navigate,waypoint))

        self.assertEqual(self.event_count[EventName.steer],1,"expected steer event following navigate")
        self.assertEqual(self.last_listened_event.heading,expected_bearing)
        self.mock_logger.info.assert_any_call('Navigator, steering to {:+f},{:+f}, bearing {:5.1f}, distance {:.1f}m'
            .format(waypoint.latitude,waypoint.longitude,expected_bearing,expected_distance))

    def test_should_steer_to_waypoint_if_outside_tolerance(self):
        self.listen(EventName.steer)
        waypoint = Waypoint(Position(53.0001,-1.9999),5)
        expected_bearing = self.globe.bearing(self.current_position,waypoint.position)

        navigator = Navigator(self.mock_gps,self.mock_helm,self.globe, self.exchange, self.mock_logger, self.config)
        self.exchange.publish(Event(EventName.navigate,waypoint))

        self.assertEqual(self.event_count[EventName.steer],1,"expected steer event following navigate")
        self.assertEqual(self.last_listened_event.heading,expected_bearing)

    def test_at_intermediate_point_should_adjust_heading(self):
        self.listen(EventName.steer)
        waypoint = Waypoint(Position(11,11),0)
        intermediate_position = Position(12,12)
        fake_gps = FakeMovingGPS([self.current_position, intermediate_position, waypoint.position])
        bearing1 = self.globe.bearing(self.current_position,waypoint.position)
        bearing2 = self.globe.bearing(intermediate_position,waypoint.position)

        navigator = Navigator(fake_gps,self.mock_helm,self.globe, self.exchange, self.mock_logger, self.config)

        self.exchange.publish(Event(EventName.navigate,waypoint))
        self.assertEqual(self.last_listened_event.heading,bearing1)

        self.exchange.publish(Event(EventName.navigate_review))
        self.assertEqual(self.event_count[EventName.steer],2,"expected 2 steer events")

        self.assertEqual(self.last_listened_event.heading,bearing2)

    def test_should_not_fire_a_steer_event_if_no_GPS_signal(self):
        self.listen(EventName.steer)
        waypoint = Waypoint(Position(-60,22),0)
        no_position = Position(NaN,NaN,NaN,NaN)
        first_bearing = self.globe.bearing(self.current_position,waypoint.position)
        fake_gps = FakeMovingGPS([self.current_position, no_position, waypoint.position])
        navigator = Navigator(fake_gps,self.mock_helm,self.globe, self.exchange, self.mock_logger, self.config)

        self.exchange.publish(Event(EventName.navigate,waypoint))
        self.exchange.publish(Event(EventName.navigate_review))

        steer_events = self.event_count[EventName.steer]
        self.assertEqual(steer_events,1,"expected only 1 steer event, got {0}".format(steer_events))
        self.assertEqual(self.last_listened_event.heading,first_bearing)

    # def test_should_ask_helm_to_steer_course_to_three_quaters_of_distance_to_way_point_based_on_speed(self):
    #     waypoint = Waypoint(Position(53.0001,-1.999699),5) #23m from current position
    #     bearing = self.globe.bearing(self.current_position,waypoint.position)
    #     fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
    #     navigator = Navigator(fake_gps,self.mock_helm,self.globe, self.mock_logger, self.config)
    #     for_expected_seconds = int(0.75 * time_to_destination(self.current_position,waypoint.position,fake_gps.speed))
    #
    #     navigator.to(waypoint)
    #
    #     self.mock_helm.steer_course.assert_called_with(bearing,for_expected_seconds)
    #
    # def test_should_return_minimum_steer_time_if_time_calculation_results_in_NaN(self):
    #     waypoint = Waypoint(Position(-60,22),0)
    #     no_position = Position(NaN,NaN,NaN,NaN)
    #     fake_gps = FakeMovingGPS([self.current_position, no_position, waypoint.position])
    #     expected_bearing = self.globe.bearing(self.current_position,waypoint.position)
    #
    #     navigator = Navigator(fake_gps,self.mock_helm,self.globe, Mock(), self.config)
    #     navigator.to(waypoint)
    #
    #     self.mock_helm.steer_course.assert_has_calls([
    #         call(expected_bearing,MAX_TIME_TO_STEER),
    #         call(expected_bearing,MIN_TIME_TO_STEER)])
    #
    # def test_should_use_minimum_steer_time_if_time_calculation_returns_small_value(self):
    #     waypoint = Waypoint(Position(53.0001,-1.9999),5)
    #     fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
    #     fake_gps.speed = 100
    #     expected_bearing = self.globe.bearing(self.current_position,waypoint.position)
    #
    #     navigator = Navigator(fake_gps,self.mock_helm,self.globe, self.mock_logger, self.config)
    #     navigator.to(waypoint)
    #
    #     self.mock_helm.steer_course.assert_called_with(expected_bearing,MIN_TIME_TO_STEER)
    #
    # def test_should_use_maximum_steer_time_if_its_a_long_way_to_go(self):
    #     waypoint = Waypoint(Position(60.0001,10),5)
    #     fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
    #     fake_gps.speed = 1
    #     expected_bearing = self.globe.bearing(self.current_position,waypoint.position)
    #
    #     navigator = Navigator(fake_gps,self.mock_helm,self.globe, self.mock_logger, self.config)
    #     navigator.to(waypoint)
    #
    #     self.mock_helm.steer_course.assert_called_with(expected_bearing,MAX_TIME_TO_STEER)
    #
    # def test_should_use_a_minimum_speed_for_calculation_preventing_divide_by_zero_error(self):
    #     waypoint = Waypoint(Position(53.001,-2.001),5)
    #     fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
    #     fake_gps.speed = 0
    #     expected_bearing = self.globe.bearing(self.current_position,waypoint.position)
    #     expected_time = expected_time_to_steer(self.current_position,waypoint.position,0.01)
    #
    #     navigator = Navigator(fake_gps,self.mock_helm,self.globe, self.mock_logger, self.config)
    #     navigator.to(waypoint)
    #
    #     self.mock_helm.steer_course.assert_called_with(expected_bearing,expected_time)
    #
    def test_should_return_false_for_arrived_if_current_position_is_NaN(self):
        navigator = Navigator(Mock(),self.mock_helm,self.globe, self.exchange, self.mock_logger, self.config)
        destination = Waypoint(Position(53.001,-2.001),5)
        nan_position = Position(NaN,NaN,NaN,NaN)
        self.assertFalse(navigator._arrived(nan_position, destination))


if __name__ == "__main__":
    unittest.main()
