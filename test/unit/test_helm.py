from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, PropertyMock, call
from helm import Helm
from config import CONFIG
from nan import NaN
from events import Exchange, Event,EventName
from test_utils import EventTestCase

FULL_DEFLECTION = CONFIG['helm']['full deflection']

class TestHelm(EventTestCase):

    def setUp(self):
        super(TestHelm, self).setUp()
        self.sensors = Mock()
        self.servo = Mock()
        self.logger = Mock()
        self.helm = Helm(self.exchange, self.sensors,self.servo,self.logger, CONFIG['helm'])
        self.helm.previous_track = 180

    def currently_tracking(self,previous_track, current_track, rudder_angle=0):
        self.helm.rudder_angle = rudder_angle
        self.sensors.track = current_track
        self.helm.previous_track = previous_track
        self.servo.set_position.reset_mock()

    def test_should_save_the_new_course_and_start_steering_in_that_direction(self):
        self.currently_tracking(0,0)
        self.exchange.publish(Event(EventName.set_course,heading=90))
        self.servo.set_position.assert_called_with(-30)

    def test_should_review_and_change_steering_when_steer_event_called_via_tick(self):
        self.currently_tracking(204,200)
        self.exchange.publish(Event(EventName.set_course,heading=196))
        self.assertFalse(self.servo.set_position.called)

        self.sensors.track = 200
        self.helm.previous_track = 220
        self.exchange.publish(Event(EventName.tick))
        self.servo.set_position.assert_called_with(-16)

    def test_should_review_the_course_every_tick_using_instant_values_when_turning(self):
        self.currently_tracking(80,90)
        self.exchange.publish(Event(EventName.set_course,heading=180))

        self.exchange.publish(Event(EventName.tick))
        self.servo.set_position.assert_called_with(-30)

    def test_should_review_the_course_every_10_seconds_using_average_values_when_on_course(self):
        self.currently_tracking(90,90)
        self.exchange.publish(Event(EventName.set_course,heading=90))

        self.exchange.publish(Event(EventName.tick))
        self.assertFalse(self.servo.set_position.called)


    def ignore_should_switch_to_on_course_once_pointing_in_the_right_direction(self):
        pass

    def ignore_should_switch_to_turning_if_suddenly_thrown_off_course(self):
        pass

    def ignore_should_immediately_change_to_turning_when_course_is_set(self):
        pass

    def test_should_not_change_direction_if_within_five_degrees_of_right_course_and_rate_of_turn_less_that_five_degrees(self):
        self.currently_tracking(204,200)
        self.exchange.publish(Event(EventName.set_course,heading=196))
        self.assertEqual(self.servo.set_position.call_count,0)

    def test_should_move_rudder_right_by_difference_between_heading_and_course_if_no_rate_of_turn(self):
        self.currently_tracking(200,200)
        self.exchange.publish(Event(EventName.set_course,heading=209))
        self.servo.set_position.assert_called_with(-9)

    def test_should_move_rudder_right_by_difference_between_heading_and_course_subtracting_rate_of_turn(self):
        self.currently_tracking(195,200)
        self.exchange.publish(Event(EventName.set_course,heading=209))
        self.servo.set_position.assert_called_with(-4)

    def test_should_move_rudder_left_by_difference_between_heading_and_course_subtracting_larger_rate_of_turn(self):
        self.currently_tracking(190,205)
        self.exchange.publish(Event(EventName.set_course,heading=209))
        self.servo.set_position.assert_called_with(11)

    def test_should_move_rudder_left_by_difference_between_heading_and_course_subtracting_rate_of_turn(self):
        self.currently_tracking(20,10)
        self.exchange.publish(Event(EventName.set_course,heading=355))
        self.servo.set_position.assert_called_with(5)

    def test_rudder_movements_should_be_relative_to_current_rudder_position(self):
        self.currently_tracking(20,10,5)
        self.exchange.publish(Event(EventName.set_course,heading=355))
        self.servo.set_position.assert_called_with(10)

    def test_rudder_movements_should_be_limited_to_full_deflection_left(self):
        self.currently_tracking(20,10,5)
        self.exchange.publish(Event(EventName.set_course,heading=330))
        self.servo.set_position.assert_called_with(FULL_DEFLECTION)

    def test_rudder_movements_should_be_limited_to_full_deflection_right(self):
        self.currently_tracking(355,355,-20)
        self.exchange.publish(Event(EventName.set_course,heading=20))
        self.servo.set_position.assert_called_with(-FULL_DEFLECTION)

    def test_should_steer_left_if_difference_is_less_than_180(self):
        self.currently_tracking(200,200)
        self.exchange.publish(Event(EventName.set_course,heading=45))
        self.servo.set_position.assert_called_with(FULL_DEFLECTION)

    def test_should_steer_right_if_difference_is_less_than_180(self):
        self.currently_tracking(200,200)
        self.exchange.publish(Event(EventName.set_course,heading=10))
        self.servo.set_position.assert_called_with(-FULL_DEFLECTION)

    def test_should_steer_right_if_difference_is_exactly_180(self):
        self.currently_tracking(200,200)
        self.exchange.publish(Event(EventName.set_course,heading=20))
        self.servo.set_position.assert_called_with(-FULL_DEFLECTION)

    def test_should_work_with_fractional_parts(self):
        self.currently_tracking(0.9,0.9)
        self.exchange.publish(Event(EventName.set_course,heading=29.4))
        self.servo.set_position.assert_called_with(-28.5)

    def test_should_centralise_rudder_if_sensor_returns_NaN(self):
        self.sensors.track = NaN
        self.exchange.publish(Event(EventName.set_course,heading=57.23))
        self.servo.set_position.assert_called_with(0)

    def test_should_log_steering_calculation_and_status_to_debug(self):
        self.currently_tracking(20,10)
        self.exchange.publish(Event(EventName.set_course,heading=355))
        self.logger.debug.assert_called_with("Helm, steering 355.0, tracking 10.0, rate of turn -10.0, rudder +0.0, new rudder +5.0")
        self.servo.set_position.assert_called_with(5)
