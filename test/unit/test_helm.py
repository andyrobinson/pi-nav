from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call
from helm import Helm,FULL_LEFT

class TestHelm(unittest.TestCase):
    
    def setUp(self):
        self.direction = 200
        self.sensors = Mock()
        self.servo = Mock()

        self.helm = Helm(self.sensors,self.servo)

    def test_should_not_change_direction_if_within_five_degrees_of_right_course(self):
        self.sensors.track = self.direction
        self.helm.steer(self.direction + 3)
        self.assertEqual(self.servo.set_position.call_count,0)
    
    def test_should_steer_left_if_difference_is_less_than_180(self):
        self.sensors.track = self.direction
        self.helm.steer(45)

        self.servo.set_position.assert_called_with(FULL_LEFT)

    def test_should_steer_left_if_difference_is_less_than_180_but_straddles_zero(self):
        self.sensors.track = 10
        self.helm.steer(320)
        self.servo.set_position.assert_called_with(FULL_LEFT)

    def test_heading_difference_should_produce_value_between_zero_and_minus_180_when_turning_left(self):
        self.assertEqual(self.helm._angular_diff(0,0),0)
        self.assertEqual(self.helm._angular_diff(1,0),-1)
        self.assertEqual(self.helm._angular_diff(90,0),-90)
        self.assertEqual(self.helm._angular_diff(180,1),-179)
        self.assertEqual(self.helm._angular_diff(359,270),-89)
        self.assertEqual(self.helm._angular_diff(360,270),-90)

    def test_heading_difference_should_produce_value_between_zero_and_minus_180_when_turning_left_across_due_north(self):
        self.assertEqual(self.helm._angular_diff(0,359),-1)
        self.assertEqual(self.helm._angular_diff(0,270),-90)
        self.assertEqual(self.helm._angular_diff(1,270),-91)
        self.assertEqual(self.helm._angular_diff(180,1),-179)
        self.assertEqual(self.helm._angular_diff(1,182),-179)

    def test_heading_difference_should_produce_value_between_zero_and_180_when_turning_right(self):
        self.assertEqual(self.helm._angular_diff(0,1),1)
        self.assertEqual(self.helm._angular_diff(0,90),90)
        self.assertEqual(self.helm._angular_diff(1,180),179)
        self.assertEqual(self.helm._angular_diff(181,0),179)
        self.assertEqual(self.helm._angular_diff(300,320),20)

    def test_heading_difference_should_produce_value_between_zero_and_180_when_turning_right_across_due_north(self):
        self.assertEqual(self.helm._angular_diff(270,0),90)
        self.assertEqual(self.helm._angular_diff(359,1),2)
        self.assertEqual(self.helm._angular_diff(359,178),179)
        self.assertEqual(self.helm._angular_diff(181,0),179)
        self.assertEqual(self.helm._angular_diff(181,360),179)
        self.assertEqual(self.helm._angular_diff(181,270),89)
        self.assertEqual(self.helm._angular_diff(270,89),179)

    def test_heading_should_be_positive_for_180_turns(self):
        self.assertEqual(self.helm._angular_diff(1,181),180)
        self.assertEqual(self.helm._angular_diff(181,1),180)
        self.assertEqual(self.helm._angular_diff(180,0),180)
        self.assertEqual(self.helm._angular_diff(0,180),180)
        self.assertEqual(self.helm._angular_diff(90,270),180)
        self.assertEqual(self.helm._angular_diff(270,90),180)
        self.assertEqual(self.helm._angular_diff(360,180),180)
        self.assertEqual(self.helm._angular_diff(360,180),180)
        self.assertEqual(self.helm._angular_diff(179,359),180)
        self.assertEqual(self.helm._angular_diff(359,179),180)

