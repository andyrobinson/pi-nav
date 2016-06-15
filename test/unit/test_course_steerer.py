from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call
from course_steerer import CourseSteerer
from config import CONFIG

FULL_DEFLECTION = CONFIG['steerer']['full rudder deflection']

class TestCourseSteerer(unittest.TestCase):

    def setUp(self):
        self.sensors = Mock()
        self.sensors.wind_direction = 0
        self.timer = Mock()
        self.helm = Mock()
        self.course_steerer = CourseSteerer(self.sensors,self.helm,self.timer,CONFIG['course steerer'])

    def test_should_return_immediately_if_time_has_expired(self):
        self.sensors.track = 200
        required_course = 180
        for_zero_seconds = 0

        self.course_steerer.steer_course(required_course,for_zero_seconds)

        self.assertEqual(self.helm.steer.call_count,0)

    def test_should_steer_and_wait_for_one_second_if_time_has_not_expired(self):
        required_course = 180
        for_one_second = 1

        self.course_steerer.steer_course(required_course,for_one_second)

        self.helm.steer.assert_called_with(180)
        self.timer.wait_for.assert_called_with(1)

    def test_should_steer_repeatedly_and_with_greater_deflection_to_max_until_time_has_expired(self):
        required_course = 180
        for_seconds = 4

        self.course_steerer.steer_course(required_course,for_seconds)

        self.helm.steer.assert_has_calls([call(180),call(180),call(180),call(180)])
        self.timer.wait_for.assert_has_calls([call(1),call(1),call(1)])

    def test_should_not_steer_right_into_the_no_go_zone(self):
        self.sensors.wind_direction = 225
        required_course = 190
        for_seconds = 2
        no_go_angle = 45

        self.course_steerer.steer_course(required_course,for_seconds,no_go_angle)

        self.helm.steer.assert_has_calls([call(180),call(180)])
        self.timer.wait_for.assert_has_calls([call(1),call(1)])

    def test_should_not_steer_left_into_the_no_go_zone(self):
        self.sensors.wind_direction = 135
        required_course = 170
        for_seconds = 2
        no_go_angle = 45

        self.course_steerer.steer_course(required_course,for_seconds,no_go_angle)

        self.helm.steer.assert_has_calls([call(180),call(180)])
        self.timer.wait_for.assert_has_calls([call(1),call(1)])
