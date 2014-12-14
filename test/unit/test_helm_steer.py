from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call
from helm import Helm
from config import CONFIG
from nan import NaN

FULL_DEFLECTION = CONFIG['helm']['full deflection']

class TestHelm(unittest.TestCase):
    
    def setUp(self):
        self.sensors = Mock()
        self.servo = Mock()
        timer = Mock()
        self.helm = Helm(self.sensors,self.servo,timer,CONFIG['helm'])
        self.helm.previous_track = 180

    def currently_tracking(self,previous_track, current_track, rudder_angle=0):
        self.helm.rudder_angle = rudder_angle
        self.sensors.track = current_track
        self.helm.previous_track = previous_track
        self.servo.set_position.reset_mock()

    def test_should_not_change_direction_if_within_five_degrees_of_right_course_and_rate_of_turn_less_that_five_degrees(self):
        self.currently_tracking(204,200)
        self.helm.steer(203)
        self.assertEqual(self.servo.set_position.call_count,0)

    def test_should_move_rudder_right_by_difference_between_heading_and_course_if_no_rate_of_turn(self):
        self.currently_tracking(200,200)
        self.helm.steer(209)
        self.servo.set_position.assert_called_with(9)

    def test_should_move_rudder_right_by_difference_between_heading_and_course_subtracting_rate_of_turn(self):
        self.currently_tracking(195,200)
        self.helm.steer(209)
        self.servo.set_position.assert_called_with(4)

    def test_should_move_rudder_left_by_difference_between_heading_and_course_subtracting_larger_rate_of_turn(self):
        self.currently_tracking(190,205)
        self.helm.steer(209)
        self.servo.set_position.assert_called_with(-11)

    def test_should_move_rudder_left_by_difference_between_heading_and_course_subtracting_rate_of_turn(self):
        self.currently_tracking(20,10)
        self.helm.steer(355)
        self.servo.set_position.assert_called_with(-5)

    def test_rudder_movements_should_be_relative_to_current_rudder_position(self):
        self.currently_tracking(20,10,-5)
        self.helm.steer(355)
        self.servo.set_position.assert_called_with(-10)

    def test_rudder_movements_should_be_limited_to_full_deflection_left(self):
        self.currently_tracking(20,10,-5)
        self.helm.steer(330)
        self.servo.set_position.assert_called_with(-FULL_DEFLECTION)

    def test_rudder_movements_should_be_limited_to_full_deflection_right(self):
        self.currently_tracking(355,355,20)
        self.helm.steer(20)
        self.servo.set_position.assert_called_with(FULL_DEFLECTION)

    def test_should_steer_left_if_difference_is_less_than_180(self):
        self.currently_tracking(200,200)
        self.helm.steer(45)
        self.servo.set_position.assert_called_with(-FULL_DEFLECTION)

    def test_should_steer_right_if_difference_is_less_than_180(self):
        self.currently_tracking(200,200)
        self.helm.steer(10)
        self.servo.set_position.assert_called_with(FULL_DEFLECTION)

    def test_should_steer_right_if_difference_is_exactly_180(self):
        self.currently_tracking(200,200)
        self.helm.steer(20)
        self.servo.set_position.assert_called_with(FULL_DEFLECTION)

    def test_should_work_with_fractional_parts(self):
        self.currently_tracking(0.9,0.9)
        self.helm.steer(29.4)
        self.servo.set_position.assert_called_with(28.5)

    def test_should_centralise_rudder_if_sensor_returns_NaN(self):
        self.sensors.track = NaN
        self.helm.steer(57.23)

        self.servo.set_position.assert_called_with(0)
