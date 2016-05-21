from setup_test import setup_test
setup_test()
import unittest
import logging
from mock import Mock, call
from fake_moving_gps import FakeMovingGPS

from navigator import Navigator
from globe import Globe
from position import Position
from waypoint import Waypoint
from nan import NaN, isNaN
from events import Exchange, Event,EventName
from test_utils import EventTestCase

MIN_TIME_TO_STEER = 7
MAX_TIME_TO_STEER = 200000

def last_called_args(mock):
    return mock.call_args[0]

def time_to_destination(position, destination, speed):
    globe = Globe()
    distance = globe.distance_between(position, destination)
    return distance /speed

def expected_time_to_steer(position, destination, speed):
    return int(0.5 * time_to_destination(position, destination, speed))

class TestNavigator(EventTestCase):

    def new_navigator(self,gps):
        return Navigator(gps,self.globe, self.exchange, self.mock_logger, self.config)

    def setUp(self):
        super(TestNavigator, self).setUp()
        self.current_position = Position(53,-2,5,5)
        self.mock_gps = Mock(position=self.current_position,speed=1)
        self.globe = Globe()
        self.mock_logger = Mock()
        self.config = {'min time to steer' : MIN_TIME_TO_STEER, 'max time to steer' : MAX_TIME_TO_STEER}

    def test_should_not_steer_and_log_arrival_if_arrived(self):
        self.listen(EventName.arrived)
        self.listen(EventName.set_course)
        navigator = self.new_navigator(self.mock_gps)

        self.exchange.publish(Event(EventName.navigate,Waypoint(self.current_position,0)))

        self.assertEqual(self.event_count(EventName.set_course),0,"expected no event to set course if we have arrived")
        self.assertEqual(self.event_count(EventName.arrived),1,"expected arrived event if we have arrived")
        self.mock_logger.info.assert_called_with('Navigator, arrived at {:+f},{:+f}'.format(self.current_position.latitude,self.current_position.longitude))

    def test_should_allow_a_tolerance_and_consider_errors_when_calculating_if_we_have_reached_waypoint(self):
        self.listen(EventName.arrived)
        self.listen(EventName.set_course)
        waypoint = Waypoint(Position(53.0001,-1.9999),10)
        navigator = self.new_navigator(self.mock_gps)

        self.exchange.publish(Event(EventName.navigate,waypoint))

        self.assertEqual(self.event_count(EventName.arrived),1,"expected arrived event if we have arrived")
        self.mock_logger.info.assert_called_with('Navigator, arrived at {:+f},{:+f}'.format(waypoint.latitude,waypoint.longitude))

    def test_should_steer_along_the_bearing_to_the_next_waypoint(self):
        self.listen(EventName.set_course)
        waypoint = Waypoint(Position(53.5,-1.5),0)
        expected_distance = self.globe.distance_between(self.current_position,waypoint.position)
        expected_bearing = self.globe.bearing(self.current_position,waypoint.position)

        navigator = self.new_navigator(self.mock_gps)
        self.exchange.publish(Event(EventName.navigate,waypoint))

        self.assertEqual(self.event_count(EventName.set_course),1,"expected set course event following navigate")
        self.assertEqual(self.last_event.heading,expected_bearing)
        self.mock_logger.info.assert_any_call('Navigator, steering to {:+f},{:+f}, bearing {:5.1f}, distance {:.1f}m'
            .format(waypoint.latitude,waypoint.longitude,expected_bearing,expected_distance))

    def test_should_steer_to_waypoint_if_outside_tolerance(self):
        self.listen(EventName.set_course)
        waypoint = Waypoint(Position(53.0001,-1.9999),5)
        expected_bearing = self.globe.bearing(self.current_position,waypoint.position)

        navigator = self.new_navigator(self.mock_gps)
        self.exchange.publish(Event(EventName.navigate,waypoint))

        self.assertEqual(self.event_count(EventName.set_course),1,"expected set course event following navigate")
        self.assertEqual(self.last_event.heading,expected_bearing)

    def test_at_intermediate_point_should_adjust_heading(self):
        self.listen(EventName.set_course)
        waypoint = Waypoint(Position(11,11),0)
        intermediate_position = Position(12,12)
        fake_gps = FakeMovingGPS([self.current_position, intermediate_position, waypoint.position])
        bearing1 = self.globe.bearing(self.current_position,waypoint.position)
        bearing2 = self.globe.bearing(intermediate_position,waypoint.position)

        navigator = self.new_navigator(fake_gps)
        self.exchange.publish(Event(EventName.navigate,waypoint))

        self.assertEqual(self.last_event.heading,bearing1)

        self.exchange.publish(Event(EventName.navigate_review))
        self.assertEqual(self.event_count(EventName.set_course),2,"expected 2 set course events")
        self.assertEqual(self.last_event.heading,bearing2)

    def test_should_not_fire_a_steer_event_if_no_GPS_signal(self):
        self.listen(EventName.set_course)
        waypoint = Waypoint(Position(-60,22),0)
        no_position = Position(NaN,NaN,NaN,NaN)
        first_bearing = self.globe.bearing(self.current_position,waypoint.position)
        fake_gps = FakeMovingGPS([self.current_position, no_position, waypoint.position])

        navigator = self.new_navigator(fake_gps)
        self.exchange.publish(Event(EventName.navigate,waypoint))
        self.exchange.publish(Event(EventName.navigate_review))

        steer_events = self.event_count(EventName.set_course)
        self.assertEqual(steer_events,1,"expected only 1 set course event, got {0}".format(steer_events))
        self.assertEqual(self.last_event.heading,first_bearing)

    def test_should_signal_review_after_half_way_to_way_point_based_on_speed(self):
        self.listen(EventName.after)
        waypoint = Waypoint(Position(53.0001,-1.999699),5) #23m from current position
        bearing = self.globe.bearing(self.current_position,waypoint.position)
        fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
        for_expected_seconds = int(0.5 * time_to_destination(self.current_position,waypoint.position,fake_gps.speed))

        navigator = self.new_navigator(fake_gps)
        self.exchange.publish(Event(EventName.navigate,waypoint))

        self.assertEqual(self.event_count(EventName.after),1,"expected 1 'after' event")
        self.assertEqual(self.last_event.name,EventName.after)
        self.assertEqual(self.last_event.seconds,for_expected_seconds)
        self.assertEqual(self.last_event.next_event.name,EventName.navigate_review)

    def test_should_return_minimum_review_time_if_time_calculation_results_in_NaN(self):
        self.listen(EventName.after)
        waypoint = Waypoint(Position(-60,22),0)
        no_position = Position(NaN,NaN,NaN,NaN)
        fake_gps = FakeMovingGPS([self.current_position, no_position, waypoint.position])
        navigator = self.new_navigator(fake_gps)
        self.exchange.publish(Event(EventName.navigate,waypoint))

        self.assertEqual(self.last_event.seconds,MAX_TIME_TO_STEER)
        self.exchange.publish(Event(EventName.navigate_review,waypoint))

        self.assertEqual(self.event_count(EventName.after),2,"expected 1 'after' events")
        self.assertEqual(self.last_event.seconds,MIN_TIME_TO_STEER)

    def test_should_use_minimum_steer_time_if_time_calculation_returns_small_value(self):
        self.listen(EventName.after)
        waypoint = Waypoint(Position(53.0001,-1.9999),5)
        fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
        fake_gps.speed = 100

        navigator = self.new_navigator(fake_gps)
        self.exchange.publish(Event(EventName.navigate,waypoint))

        self.assertEqual(self.last_event.seconds,MIN_TIME_TO_STEER)

    def test_should_use_maximum_steer_time_if_its_a_long_way_to_go(self):
        self.listen(EventName.after)
        waypoint = Waypoint(Position(60.0001,10),5)
        fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
        fake_gps.speed = 1
        expected_bearing = self.globe.bearing(self.current_position,waypoint.position)

        navigator = self.new_navigator(fake_gps)
        self.exchange.publish(Event(EventName.navigate,waypoint))

        self.assertEqual(self.last_event.seconds,MAX_TIME_TO_STEER)

    def test_should_use_a_minimum_speed_for_calculation_preventing_divide_by_zero_error(self):
        self.listen(EventName.after)
        waypoint = Waypoint(Position(53.001,-2.001),5)
        fake_gps = FakeMovingGPS([self.current_position, waypoint.position])
        fake_gps.speed = 0
        expected_time = expected_time_to_steer(self.current_position,waypoint.position,0.01)

        navigator = self.new_navigator(fake_gps)
        self.exchange.publish(Event(EventName.navigate,waypoint))

        self.assertEqual(self.last_event.seconds,expected_time)

    def test_should_return_false_for_arrived_if_current_position_is_NaN(self):
        navigator = self.new_navigator(Mock())
        destination = Waypoint(Position(53.001,-2.001),5)
        nan_position = Position(NaN,NaN,NaN,NaN)
        self.assertFalse(navigator._arrived(nan_position, destination))
