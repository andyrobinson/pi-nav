from setup_test import setup_test
setup_test()
import unittest
from math import sin,radians
from mock import Mock, call
from sailing_helm import SailingHelm

class TestSailingHelm(unittest.TestCase):

    def setUp(self):
        config = {'no go angle': 50,
                  'min tack duration': 5}
        self.no_go = config['no go angle']
        self.course_steerer = Mock()
        self.sensors = Mock()
        self.sailing_helm = SailingHelm(self.sensors,self.course_steerer,config)

    def test_sail_directly_if_wind_not_in_no_go_zone(self):
        self.sensors.wind_direction = 270
        self.sailing_helm.steer_course(90,10)
        self.course_steerer.steer_course.assert_called_with(90,10,self.no_go)

        self.sensors.wind_direction = 39
        self.sailing_helm.steer_course(90,10)
        self.course_steerer.steer_course.assert_called_with(90,10,self.no_go)

        self.sensors.wind_direction = 141
        self.sailing_helm.steer_course(90,10)
        self.course_steerer.steer_course.assert_called_with(90,10,self.no_go)

    def test_should_tack_left_then_right_equally_if_wind_straight_ahead(self):
        self.sensors.wind_direction = 190
        self.sailing_helm.steer_course(190,150)
        self.course_steerer.steer_course.assert_has_calls([call(140.0,117,self.no_go),call(240.0,117,self.no_go)])

    def test_should_tack_right_first_and_longer_then_left_if_wind_in_no_go_to_left_of_centre(self):
        self.sensors.wind_direction = 350
        self.sailing_helm.steer_course(10,200)
        self.course_steerer.steer_course.assert_has_calls([call(40.0, 191.0,self.no_go), call(300, 102.0,self.no_go)])

    def test_should_tack_left_first_and_longer_then_right_if_wind_in_no_go_to_right_of_centre(self):
        self.sensors.wind_direction = 5
        self.sailing_helm.steer_course(345,120)
        self.course_steerer.steer_course.assert_has_calls([call(315.0, 115.0,self.no_go), call(55.0, 61.0,self.no_go)])

    def test_should_calculate_length_of_tacks_based_on_angle_total_sailing_time_and_no_go_angle(self):
        wind_course_difference,total_time = 10,30
        results = self.sailing_helm._leg_times(wind_course_difference,total_time)
        sin_tack_angle = sin(radians(180 - (2 * self.no_go)))

        expected_first_leg_long = round(float(total_time) * sin(radians((2 * self.no_go) - wind_course_difference)) / sin_tack_angle)
        expected_second_leg_short = round(float(total_time) * sin(radians(wind_course_difference)) /sin_tack_angle)

        self.assertEqual(results,(expected_first_leg_long,expected_second_leg_short))

    def test_should_produce_zero_second_leg_if_steering_straight_ahead(self):
        self.assertEqual((20,0),self.sailing_helm._leg_times(0,20))

    def test_should_produce_equal_legs_if_steering_at_no_go_angle(self):
        self.assertEqual((16,16),self.sailing_helm._leg_times(self.no_go,20))

    def test_should_steer_left_first_using_diff_between_wind_and_course_if_wind_is_coming_from_the_right(self):
        self.assertEqual(self.sailing_helm._initial_tack_deflection(40),40 - self.no_go)

    def test_should_steer_right_first_using_diff_between_wind_and_course_if_wind_is_coming_from_the_left(self):
        self.assertEqual(self.sailing_helm._initial_tack_deflection(-30),self.no_go - 30)

    def test_should_only_perform_first_tack_if_second_tack_is_five_seconds_or_less(self):
        wind_direction = 260
        self.sensors.wind_direction = wind_direction
        self.sailing_helm.steer_course(215,30)
        self.course_steerer.steer_course.assert_called_with(210.0, 30,self.no_go)
