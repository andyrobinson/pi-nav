from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, PropertyMock, call
from helm import Helm
from config import CONFIG
from nan import NaN
from events import Exchange, Event,EventName
from test_utils import EventTestCase
from copy import deepcopy

FULL_DEFLECTION = CONFIG['helm']['full deflection']
TEST_CONFIG = deepcopy(CONFIG['helm'])
TEST_CONFIG['turn on course min count'] = 3

class TestHelm(EventTestCase):

    def setUp(self):
        super(TestHelm, self).setUp()
        self.sensors = Mock()
        self.servo = Mock()
        self.logger = Mock()
        self.helm = Helm(self.exchange, self.sensors,self.servo,self.logger, TEST_CONFIG)
        self.helm.previous_heading = 180

    def currently_tracking(self,previous_heading, current_track, rudder_angle=0):
        self.helm.rudder_angle = rudder_angle
        self.sensors.compass_heading_instant = current_track
        self.sensors.compass_heading_average = NaN
        self.sensors.rate_of_turn = current_track - previous_heading
        self.sensors.rate_of_turn_average = self.sensors.rate_of_turn
        self.helm.previous_heading = previous_heading
        self.servo.set_position.reset_mock()

    def averagely_tracking(self,previous_heading, current_track):
        self.helm.rudder_angle = 0
        self.sensors.compass_heading_average = current_track
        self.sensors.compass_heading_instant = NaN
        self.sensors.rate_of_turn = 0
        self.sensors.rate_of_turn_average = current_track - previous_heading
        self.helm.previous_heading = previous_heading
        self.servo.set_position.reset_mock()

    def test_should_review_and_change_steering_based_on_instant_heading_and_rate_of_turn_when_turning(self):
        self.currently_tracking(204,200)
        self.exchange.publish(Event(EventName.set_course,heading=196))
        self.assertFalse(self.servo.set_position.called)

        self.sensors.track = 200
        self.sensors.rate_of_turn = -20
        self.exchange.publish(Event(EventName.tick))
        self.servo.set_position.assert_called_with(-16)

    def test_should_use_instant_heading_when_turning(self):
        self.helm.requested_heading = 5
        self.currently_tracking(340,350)
        self.helm.turn(Event(EventName.tick))

        self.servo.set_position.assert_called_with(-5)

    def test_should_use_average_heading_when_checking_course(self):
        self.helm.requested_heading = 5
        self.averagely_tracking(340,350)
        self.helm.check_course(Event(EventName.tick))

        self.servo.set_position.assert_called_with(-5)

    def test_should_trigger_turning_if_off_course_by_more_than_configured_20_degrees(self):
        self.exchange.unsubscribe(EventName.tick,self.helm.turn)
        self.helm.requested_heading = 90
        self.averagely_tracking(50,60)
        self.helm.check_course(Event(EventName.tick))

        self.servo.set_position.assert_called_with(-20)
        self.assertIn(self.helm.turn,self.exchange.register[EventName.tick])

    def test_should_immediately_change_to_turning_when_course_is_set(self):
        self.exchange.unsubscribe(EventName.tick,self.helm.turn)
        self.currently_tracking(50,60)

        self.exchange.publish(Event(EventName.set_course,heading=90))

        self.servo.set_position.assert_called_with(-20)
        self.assertIn(self.helm.turn,self.exchange.register[EventName.tick])

    def test_should_unsubscribe_turn_to_tick_event_when_on_course_after_configured_three_checks(self):
        self.currently_tracking(120,125)
        self.exchange.publish(Event(EventName.set_course,heading=90))

        self.currently_tracking(95,85)
        self.exchange.publish(Event(EventName.tick))
        self.currently_tracking(85,87)
        self.exchange.publish(Event(EventName.tick))
        self.currently_tracking(85,87)
        self.exchange.publish(Event(EventName.tick))
        self.currently_tracking(85,87)
        self.exchange.publish(Event(EventName.tick))

        self.assertNotIn(self.helm.turn,self.exchange.register[EventName.tick])

    def test_should_continue_turning_if_on_course_with_high_rate_of_turn(self):
        self.currently_tracking(95,85)
        self.exchange.publish(Event(EventName.set_course,heading=90))

        self.currently_tracking(85,95)
        self.exchange.publish(Event(EventName.tick))
        self.currently_tracking(95,85)
        self.exchange.publish(Event(EventName.tick))
        self.currently_tracking(85,95)
        self.exchange.publish(Event(EventName.tick))
        self.currently_tracking(95,85)
        self.exchange.publish(Event(EventName.tick))

        self.assertIn(self.helm.turn,self.exchange.register[EventName.tick])

    def test_should_subscribe_check_course_every_10_seconds(self):
        self.listen(EventName.every)
        helm = Helm(self.exchange, self.sensors,self.servo,self.logger, TEST_CONFIG)

        self.assertEqual(len(self.events[EventName.every]),1)

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
        self.sensors.compass_heading_instant = NaN
        self.exchange.publish(Event(EventName.set_course,heading=57.23))
        self.servo.set_position.assert_called_with(0)

    def test_should_log_steering_calculation_and_status_to_debug(self):
        self.currently_tracking(20,10)
        self.exchange.publish(Event(EventName.set_course,heading=355))
        self.logger.debug.assert_called_with("Helm, steering 355.0, heading 10.0, rate of turn -10.0, rudder +0.0, new rudder +5.0")
        self.servo.set_position.assert_called_with(5)
