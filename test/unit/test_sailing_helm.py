from setup_test import setup_test
setup_test()
import unittest
from math import sin,radians
from mock import Mock, call
from sailing_helm import SailingHelm
from events import Exchange, Event,EventName
from test_utils import EventTestCase

class TestSailingHelm(EventTestCase):

    def setUp(self):
        super(TestSailingHelm, self).setUp()
        config = {'no go angle': 50, 'min tack duration': 5}
        self.no_go = config['no go angle']
        self.sensors = Mock()
        self.logger = Mock()
        self.sailing_helm = SailingHelm(self.exchange, self.sensors, self.logger, config)
        self.listen(EventName.set_course)
        self.listen(EventName.tack)
        self.listen(EventName.after)

    def test_sail_directly_if_running(self):
        self.sensors.wind_direction_abs_average = 270
        self.exchange.publish(Event(EventName.sail_course,heading=90,seconds=100))
        self.assertEqual(self.last_event, Event(EventName.set_course, heading=90))

    def test_sail_directly_if_close_hauled_outside_no_go(self):
        self.sensors.wind_direction_abs_average = 0
        self.exchange.publish(Event(EventName.sail_course,heading=51,seconds=100))
        self.assertEqual(self.last_event, Event(EventName.set_course, heading=51))

        self.sensors.wind_direction_abs_average = 0
        self.exchange.publish(Event(EventName.sail_course,heading=309,seconds=100))
        self.assertEqual(self.last_event, Event(EventName.set_course, heading=309))

    def test_should_tack_left_for_half_the_time_then_right_if_wind_straight_ahead(self):
        self.sensors.wind_direction_abs_average = 190
        self.exchange.publish(Event(EventName.sail_course,heading=190, seconds=100))

        right_tack = Event(EventName.tack, heading=240)
        left_tack = Event(EventName.tack, heading=140.0)
        self.assertEqual(self.events[EventName.tack], [left_tack])
        self.assertEqual(self.events[EventName.after],[Event(EventName.after, seconds=50, next_event=right_tack)])

    def test_should_issue_a_set_course_event_when_the_tack_event_is_fired(self):
        right_tack = Event(EventName.tack, heading=240)
        self.exchange.publish(right_tack)
        self.assertEqual(self.last_event, Event(EventName.set_course, heading=240))

    def test_should_tack_right_first_and_longer_then_left_if_wind_in_no_go_to_left_of_centre(self):
        self.sensors.wind_direction_abs_average = 350
        self.exchange.publish(Event(EventName.sail_course,heading=10, seconds=200))

        right_tack = Event(EventName.tack, heading=40)
        left_tack = Event(EventName.tack, heading=300)
        self.assertEqual(self.events[EventName.tack],[right_tack])
        self.assertEqual(self.events[EventName.after],[Event(EventName.after, seconds=131.0, next_event=left_tack)])

    def test_should_tack_left_first_and_longer_then_right_if_wind_in_no_go_to_right_of_centre(self):
        self.sensors.wind_direction_abs_average = 5
        self.exchange.publish(Event(EventName.sail_course,heading=345, seconds=120))

        left_tack = Event(EventName.tack, heading=315.0)
        right_tack = Event(EventName.tack, heading=55.0)
        self.assertEqual(self.events[EventName.tack],[left_tack])
        self.assertEqual(self.events[EventName.after],[Event(EventName.after, seconds=78.0, next_event=right_tack)])

    def ignore_should_calculate_length_of_tacks_based_on_angle_total_sailing_time_and_no_go_angle(self):
        wind_course_difference,total_time = 10,30
        results = self.sailing_helm._leg_times(wind_course_difference,total_time)
        sin_tack_angle = sin(radians(180 - (2 * self.no_go)))

        expected_first_leg_long = round(float(total_time) * sin(radians((2 * self.no_go) - wind_course_difference)) / sin_tack_angle)
        expected_second_leg_short = round(float(total_time) * sin(radians(wind_course_difference)) /sin_tack_angle)

        self.assertEqual(results,(expected_first_leg_long,expected_second_leg_short))

    def ignore_should_produce_zero_second_leg_if_steering_straight_ahead(self):
        self.assertEqual((20,0),self.sailing_helm._leg_times(0,20))

    def ignore_should_produce_equal_legs_if_steering_at_no_go_angle(self):
        self.assertEqual((16,16),self.sailing_helm._leg_times(self.no_go,20))

    def ignore_should_steer_left_first_using_diff_between_wind_and_course_if_wind_is_coming_from_the_right(self):
        self.assertEqual(self.sailing_helm._initial_tack_deflection(40),40 - self.no_go)

    def ignore_should_steer_right_first_using_diff_between_wind_and_course_if_wind_is_coming_from_the_left(self):
        self.assertEqual(self.sailing_helm._initial_tack_deflection(-30),self.no_go - 30)

    def ignore_should_only_perform_first_tack_if_second_tack_is_five_seconds_or_less(self):
        wind_direction = 260
        self.sensors.wind_direction = wind_direction
        self.sailing_helm.steer_course(215,30)
        self.course_steerer.steer_course.assert_called_with(210.0, 30,self.no_go)
