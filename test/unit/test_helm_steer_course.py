from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call
from helm import Helm
from course_steerer import CourseSteerer
from config import CONFIG

FULL_DEFLECTION = CONFIG['helm']['full deflection']

class TestHelmSteerCourse(unittest.TestCase):

    def setUp(self):
        self.sensors = Mock()
        self.sensors.wind_direction = 0
        self.servo = Mock()
        self.timer = Mock()

        self.helm = Helm(self.sensors,self.servo,self.timer,Mock(),CONFIG['helm'])
        self.course_steerer = CourseSteerer(self.sensors,self.helm,self.timer)
        self.servo.reset_mock()

    def test_should_return_immediately_if_time_has_expired(self):
        self.sensors.track = 200
        required_course = 180
        for_zero_seconds = 0

        self.course_steerer.steer_course(required_course,for_zero_seconds)

        self.assertEqual(self.servo.set_position.call_count,0)

    def test_should_steer_and_wait_for_one_second_if_time_has_not_expired(self):
        self.sensors.track = 200
        self.helm.previous_track = 200
        required_course = 180
        for_one_second = 1

        self.course_steerer.steer_course(required_course,for_one_second)

        self.servo.set_position.assert_called_with(20)
        self.timer.wait_for.assert_called_with(1)

    def test_should_steer_repeatedly_and_with_greater_deflection_to_max_until_time_has_expired(self):
        self.sensors.track = 190
        self.helm.previous_track = 195
        required_course = 180
        for_seconds = 4

        self.course_steerer.steer_course(required_course,for_seconds)

        self.servo.set_position.assert_has_calls([call(5),call(15),call(25),call(30)])
        self.timer.wait_for.assert_has_calls([call(1),call(1),call(1)])

    def test_should_not_steer_right_into_the_no_go_zone(self):
        self.sensors.track = 180
        self.sensors.wind_direction = 225
        self.helm.previous_track = 180
        required_course = 190
        for_seconds = 2
        no_go_angle = 45

        self.course_steerer.steer_course(required_course,for_seconds,no_go_angle)

        self.assertEqual(self.servo.set_position.call_count,0)
        self.timer.wait_for.assert_has_calls([call(1),call(1)])

    def test_should_not_steer_left_into_the_no_go_zone(self):
        self.sensors.track = 180
        self.sensors.wind_direction = 135
        self.helm.previous_track = 180
        required_course = 170
        for_seconds = 2
        no_go_angle = 45

        self.course_steerer.steer_course(required_course,for_seconds,no_go_angle)

        self.assertEqual(self.servo.set_position.call_count,0)
        self.timer.wait_for.assert_has_calls([call(1),call(1)])
