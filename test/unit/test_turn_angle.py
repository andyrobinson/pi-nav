from setup_test import setup_test
setup_test()
import unittest
from mock import Mock
from helm import Helm

class TestTurnCalculation(unittest.TestCase):
    
    def setUp(self):
        self.helm = Helm(Mock(),Mock(),{'full deflection': 10})

    def test_heading_difference_should_produce_value_between_zero_and_minus_180_when_turning_left(self):
        self.assertEqual(self.helm._turn_angle(0,0),0)
        self.assertEqual(self.helm._turn_angle(1,0),-1)
        self.assertEqual(self.helm._turn_angle(90,0),-90)
        self.assertEqual(self.helm._turn_angle(180,1),-179)
        self.assertEqual(self.helm._turn_angle(359,270),-89)
        self.assertEqual(self.helm._turn_angle(359,180),-179)
        self.assertEqual(self.helm._turn_angle(360,270),-90)

    def test_heading_difference_should_produce_value_between_zero_and_minus_180_when_turning_left_across_due_north(self):
        self.assertEqual(self.helm._turn_angle(0,359),-1)
        self.assertEqual(self.helm._turn_angle(0,270),-90)
        self.assertEqual(self.helm._turn_angle(1,270),-91)
        self.assertEqual(self.helm._turn_angle(180,1),-179)
        self.assertEqual(self.helm._turn_angle(1,182),-179)

    def test_heading_difference_should_produce_value_between_zero_and_180_when_turning_right(self):
        self.assertEqual(self.helm._turn_angle(0,1),1)
        self.assertEqual(self.helm._turn_angle(0,90),90)
        self.assertEqual(self.helm._turn_angle(1,180),179)
        self.assertEqual(self.helm._turn_angle(181,0),179)
        self.assertEqual(self.helm._turn_angle(300,320),20)

    def test_heading_difference_should_produce_value_between_zero_and_180_when_turning_right_across_due_north(self):
        self.assertEqual(self.helm._turn_angle(270,0),90)
        self.assertEqual(self.helm._turn_angle(359,1),2)
        self.assertEqual(self.helm._turn_angle(359,178),179)
        self.assertEqual(self.helm._turn_angle(181,0),179)
        self.assertEqual(self.helm._turn_angle(181,360),179)
        self.assertEqual(self.helm._turn_angle(181,270),89)
        self.assertEqual(self.helm._turn_angle(270,89),179)

    def test_heading_should_be_positive_for_180_turns(self):
        self.assertEqual(self.helm._turn_angle(1,181),180)
        self.assertEqual(self.helm._turn_angle(181,1),180)
        self.assertEqual(self.helm._turn_angle(180,0),180)
        self.assertEqual(self.helm._turn_angle(0,180),180)
        self.assertEqual(self.helm._turn_angle(90,270),180)
        self.assertEqual(self.helm._turn_angle(270,90),180)
        self.assertEqual(self.helm._turn_angle(360,180),180)
        self.assertEqual(self.helm._turn_angle(360,180),180)
        self.assertEqual(self.helm._turn_angle(179,359),180)
        self.assertEqual(self.helm._turn_angle(359,179),180)


