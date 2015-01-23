from setup_test import setup_test
setup_test()
import unittest
from math import tan,radians
from mock import Mock, call
from sailing_helm import SailingHelm

class TestSailingHelm(unittest.TestCase):

    def setUp(self):
        self.helm = Mock()
        self.sensors = Mock()
        self.sailing_helm = SailingHelm(self.sensors,self.helm)

    def test_sail_directly_if_wind_not_in_no_go_zone(self):
        self.sensors.wind_direction = 270
        self.sailing_helm.steer_course(90,10)
        self.helm.steer_course.assert_called_with(90,10)

        self.sensors.wind_direction = 44
        self.sailing_helm.steer_course(90,10)
        self.helm.steer_course.assert_called_with(90,10)

        self.sensors.wind_direction = 136
        self.sailing_helm.steer_course(90,10)
        self.helm.steer_course.assert_called_with(90,10)

    def test_should_tack_left_then_right_equally_if_wind_straight_ahead(self):
        self.sensors.wind_direction = 90
        self.sailing_helm.steer_course(90,20)
        self.helm.steer_course.assert_has_calls([call(45.0,10),call(135.0,10)])

    def test_should_tack_right_longer_then_left_if_wind_in_no_go_to_left_of_centre(self):
        self.sensors.wind_direction = 80
        self.sailing_helm.steer_course(90,30)
        self.helm.steer_course.assert_has_calls([call(125.0, 18.0), call(35.0, 12.0)])

    def test_should_tack_left_longer_then_right_if_wind_in_no_go_to_right_of_centre(self):
        self.sensors.wind_direction = 130
        self.sailing_helm.steer_course(90,30)
        self.helm.steer_course.assert_has_calls([call(85.0, 28.0), call(175.0, 2.0)])

    def test_should_calculate_length_of_tacks_based_on_angle_and_total_sailing_time(self):
        wind_course_difference,total_time = 10,30
        results = self.sailing_helm._leg_times(wind_course_difference,total_time)

        expected_first_leg_long = round(total_time / (1 + tan(radians(wind_course_difference))))
        expected_second_leg_short = round(total_time - expected_first_leg_long)

        self.assertEqual(results,(expected_first_leg_long,expected_second_leg_short))
        self.assertGreater(results[0],2 * results[1])

    def test_should_produce_zero_second_leg_if_steering_straight_ahead(self):
        self.assertEqual((20,0),self.sailing_helm._leg_times(0,20))

    def test_should_produce_equal_legs_if_steering_45_degress(self):
        self.assertEqual((10,10),self.sailing_helm._leg_times(45,20))

    def test_should_steer_left_first_using_diff_between_wind_and_course_if_wind_is_coming_from_the_right(self):
        self.assertEqual(self.sailing_helm._initial_tack_deflection(40),-5)

    def test_should_steer_right_first_using_diff_between_wind_and_course_if_wind_is_coming_from_the_left(self):
        self.assertEqual(self.sailing_helm._initial_tack_deflection(-30),15)