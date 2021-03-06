from setup_test import setup_test
setup_test()
import unittest
from bearing import angle_between,to_360,moving_avg

class TestBearing(unittest.TestCase):

    def test_heading_difference_should_produce_value_between_zero_and_minus_180_when_turning_left(self):
        self.assertEqual(angle_between(0,0),0)
        self.assertEqual(angle_between(1,0),-1)
        self.assertEqual(angle_between(90,0),-90)
        self.assertEqual(angle_between(180,1),-179)
        self.assertEqual(angle_between(359,270),-89)
        self.assertEqual(angle_between(359,180),-179)
        self.assertEqual(angle_between(360,270),-90)

    def test_heading_difference_should_produce_value_between_zero_and_minus_180_when_turning_left_across_due_north(self):
        self.assertEqual(angle_between(0,359),-1)
        self.assertEqual(angle_between(0,270),-90)
        self.assertEqual(angle_between(1,270),-91)
        self.assertEqual(angle_between(180,1),-179)
        self.assertEqual(angle_between(1,182),-179)

    def test_heading_difference_should_produce_value_between_zero_and_180_when_turning_right(self):
        self.assertEqual(angle_between(0,1),1)
        self.assertEqual(angle_between(0,90),90)
        self.assertEqual(angle_between(1,180),179)
        self.assertEqual(angle_between(181,0),179)
        self.assertEqual(angle_between(300,320),20)

    def test_heading_difference_should_produce_value_between_zero_and_180_when_turning_right_across_due_north(self):
        self.assertEqual(angle_between(270,0),90)
        self.assertEqual(angle_between(359,1),2)
        self.assertEqual(angle_between(359,178),179)
        self.assertEqual(angle_between(181,0),179)
        self.assertEqual(angle_between(181,360),179)
        self.assertEqual(angle_between(181,270),89)
        self.assertEqual(angle_between(270,89),179)

    def test_heading_should_be_positive_for_180_turns(self):
        self.assertEqual(angle_between(1,181),180)
        self.assertEqual(angle_between(181,1),180)
        self.assertEqual(angle_between(180,0),180)
        self.assertEqual(angle_between(0,180),180)
        self.assertEqual(angle_between(90,270),180)
        self.assertEqual(angle_between(270,90),180)
        self.assertEqual(angle_between(360,180),180)
        self.assertEqual(angle_between(360,180),180)
        self.assertEqual(angle_between(179,359),180)
        self.assertEqual(angle_between(359,179),180)

    def test_to_360_should_leave_alone_positive_values_less_than_360(self):
        self.assertEqual(to_360(5),5)
        self.assertEqual(to_360(177),177)
        self.assertEqual(to_360(359),359)

    def test_to_360_should_add_360_to_values_less_than_zero(self):
        self.assertEqual(to_360(-5),355)
        self.assertEqual(to_360(-89),271)
        self.assertEqual(to_360(-177),183)

    def test_to_360_should_make_360_zero_as_they_are_the_same(self):
        self.assertEqual(to_360(0),0)
        self.assertEqual(to_360(360),0)

    def test_to_360_should_subtract_360_from_values_greater_than_360(self):
        self.assertEqual(to_360(380),20)
        self.assertEqual(to_360(800),80)
        self.assertEqual(to_360(719),359)

    def test_moving_average_should_move_the_average_clockwise_if_next_sample_greater(self):
        self.assertEqual(moving_avg(10,20,2),15)
        self.assertEqual(moving_avg(10,180,2),95)
        self.assertEqual(moving_avg(180.0,355.0,2),267.5)
        self.assertEqual(moving_avg(340,20.0,2),0.0)

    def test_moving_average_should_move_the_average_anitclockwise_if_next_sample_less(self):
        self.assertEqual(moving_avg(20,10,2),15)
        self.assertEqual(moving_avg(180,10,2),95)
        self.assertEqual(moving_avg(355.0,180.0,2),267.5)
        self.assertEqual(moving_avg(20,350.0,6),15.0)
