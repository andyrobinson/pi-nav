from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, PropertyMock, call
from config import CONFIG
from nan import NaN
from copy import deepcopy
from steerer import Steerer

FULL_DEFLECTION = CONFIG['helm']['full deflection']

class TestSteerer(unittest.TestCase):

    def setUp(self):
        self.servo = Mock()
        self.logger = Mock()
        self.steerer = Steerer(self.servo,self.logger, CONFIG['helm'])

    @unittest.skip("to do - course")
    def test_on_course_if_heading_and_rate_of_turn_below_threshold(self):
    # def on_course(self,requested_heading,heading,rate_of_turn):
    #     return abs(self._deviation(requested_heading,heading)) < self.ignore_below and abs(rate_of_turn) < self.ignore_below
        pass

    @unittest.skip("to do - course")
    def test_not_on_course_if_only_heading_below_threshold(self):
        pass

    @unittest.skip("to do - course")
    def test_not_on_course_if_only_rate_of_turn_below_threshold(self):
        pass

    def test_should_not_change_direction_if_within_five_degrees_of_right_course_and_rate_of_turn_less_that_five_degrees(self):
        self.steerer.steer(requested_heading=196,heading=200,rate_of_turn=4)
        self.assertEqual(self.servo.set_position.call_count,0)

    def test_should_move_rudder_right_by_difference_between_heading_and_course_if_no_rate_of_turn(self):
        self.steerer.steer(requested_heading=209,heading=200,rate_of_turn=0)
        self.servo.set_position.assert_called_with(-9)

    def test_should_move_rudder_right_by_difference_between_heading_and_course_subtracting_rate_of_turn(self):
        self.steerer.steer(requested_heading=209,heading=200,rate_of_turn=5)
        self.servo.set_position.assert_called_with(-4)

    def test_should_move_rudder_left_by_difference_between_heading_and_course_subtracting_larger_rate_of_turn(self):
        self.steerer.steer(requested_heading=209,heading=205,rate_of_turn=15)
        self.servo.set_position.assert_called_with(11)

    def test_should_move_rudder_left_by_difference_between_heading_and_course_subtracting_rate_of_turn(self):
        self.steerer.steer(requested_heading=355,heading=10,rate_of_turn=-10)
        self.servo.set_position.assert_called_with(5)

    def test_rudder_movements_should_be_relative_to_current_rudder_position(self):
        self.steerer.rudder_angle = 5
        self.steerer.steer(requested_heading=355,heading=10,rate_of_turn=-10)
        self.servo.set_position.assert_called_with(10)

    def test_rudder_movements_should_be_limited_to_full_deflection_left(self):
        self.steerer.rudder_angle = 5
        self.steerer.steer(requested_heading=330,heading=10,rate_of_turn=-10)
        self.servo.set_position.assert_called_with(FULL_DEFLECTION)

    def test_rudder_movements_should_be_limited_to_full_deflection_right(self):
        self.steerer.rudder_angle = -20
        self.steerer.steer(requested_heading=20,heading=355,rate_of_turn=0)
        self.servo.set_position.assert_called_with(-FULL_DEFLECTION)

    def test_should_steer_left_if_difference_is_less_than_180(self):
        self.steerer.steer(requested_heading=45,heading=200,rate_of_turn=0)
        self.servo.set_position.assert_called_with(FULL_DEFLECTION)

    def test_should_steer_right_if_difference_is_less_than_180(self):
        self.steerer.steer(requested_heading=10,heading=200,rate_of_turn=0)
        self.servo.set_position.assert_called_with(-FULL_DEFLECTION)

    def test_should_steer_right_if_difference_is_exactly_180(self):
        self.steerer.steer(requested_heading=20,heading=200,rate_of_turn=0)
        self.servo.set_position.assert_called_with(-FULL_DEFLECTION)

    def test_should_work_with_fractional_parts(self):
        self.steerer.steer(requested_heading=29.4,heading=0.9,rate_of_turn=0)
        self.servo.set_position.assert_called_with(-28.5)

    def test_should_centralise_rudder_if_sensor_returns_NaN(self):
        self.steerer.steer(requested_heading=57.23,heading=NaN,rate_of_turn=0)
        self.servo.set_position.assert_called_with(0)

    def test_should_log_steering_calculation_and_status_to_debug(self):
        self.steerer.steer(requested_heading=355,heading=10,rate_of_turn=-10)
        self.logger.debug.assert_called_with("Helm, steering 355.0, heading 10.0, rate of turn -10.0, rudder +0.0, new rudder +5.0")
        self.servo.set_position.assert_called_with(5)