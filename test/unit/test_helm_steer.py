from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call
from helm import Helm
from config import CONFIG

FULL_DEFLECTION = CONFIG['helm']['full deflection']

class TestHelm(unittest.TestCase):
    
    def setUp(self):
        self.sensors = Mock()
        self.servo = Mock()

        self.helm = Helm(self.sensors,self.servo, CONFIG['helm'])

    def test_should_not_change_direction_if_within_five_degrees_of_right_course_and_rudder_is_less_than_five_degrees(self):
        self.sensors.track = 200
        self.helm.rudder_angle = -1
        self.servo.set_position.reset_mock()

        self.helm.steer(203)

        self.assertEqual(self.servo.set_position.call_count,0)

    def test_should_set_the_rudder_if_track_within_five_degrees_but_still_large_rudder_deflection(self):
        self.sensors.track = 200
        self.helm.rudder_angle = 20
        self.servo.set_position.reset_mock()

        self.helm.steer(202)

        self.servo.set_position.assert_called_with(1)

    def test_should_steer_left_if_difference_is_less_than_180(self):
        self.sensors.track = 200
        self.helm.steer(45)

        self.servo.set_position.assert_called_with(-FULL_DEFLECTION)
        self.assertEqual(self.helm.rudder_angle,-FULL_DEFLECTION)

    def test_should_steer_left_if_difference_is_less_than_180_but_straddles_zero(self):
        self.sensors.track = 30
        self.helm.steer(320)
        self.servo.set_position.assert_called_with(-FULL_DEFLECTION)
        self.assertEqual(self.helm.rudder_angle,-FULL_DEFLECTION)

    def test_should_steer_right_if_difference_is_less_than_180(self):
        self.sensors.track = 200
        self.helm.steer(10)

        self.servo.set_position.assert_called_with(FULL_DEFLECTION)
        self.assertEqual(self.helm.rudder_angle,FULL_DEFLECTION)

    def test_should_steer_right_if_difference_is_exactly_180(self):
        self.sensors.track = 200
        self.helm.steer(20)

        self.servo.set_position.assert_called_with(FULL_DEFLECTION)
        self.assertEqual(self.helm.rudder_angle,FULL_DEFLECTION)

    def test_should_set_rudder_angle_at_half_of_turn_angle_if_this_is_less_than_full_deflection(self):
        self.sensors.track = 10
        self.helm.steer(52)

        self.servo.set_position.assert_called_with(21)
        self.assertEqual(self.helm.rudder_angle,21)

    def test_should_set_rudder_angle_at_full_deflection_if_turn_angle_more_than_twice_full_deflection(self):
        self.sensors.track = 0
        self.helm.steer((FULL_DEFLECTION * 2) + 2)

        self.servo.set_position.assert_called_with(FULL_DEFLECTION)
        self.assertEqual(self.helm.rudder_angle,FULL_DEFLECTION)

    def test_should_ignore_fractional_parts(self):
        self.sensors.track = 0.9
        self.helm.steer(57.23)

        self.servo.set_position.assert_called_with(28)


