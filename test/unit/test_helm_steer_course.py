from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call
from helm import Helm
from config import CONFIG

FULL_DEFLECTION = CONFIG['helm']['full deflection']

class TestHelmSteerCourse(unittest.TestCase):

    def setUp(self):
        self.sensors = Mock()
        self.servo = Mock()
        self.timer = Mock()

        self.helm = Helm(self.sensors,self.servo,self.timer,CONFIG['helm'])
        self.servo.reset_mock()

    def test_should_return_immediately_if_time_has_expired(self):
        self.sensors.track = 200
        required_course = 180
        for_zero_seconds = 0

        self.helm.steer_course(required_course,for_zero_seconds)

        self.assertEqual(self.servo.set_position.call_count,0)

    def test_should_steer_and_wait_for_one_second_if_time_has_not_expired(self):
        self.sensors.track = 200
        required_course = 180
        for_one_second = 1

        self.helm.steer_course(required_course,for_one_second)

        self.servo.set_position.assert_called_with(-10)
        self.timer.wait_for.assert_called_with(1)

    def test_should_steer_repeatedly_until_time_has_expired(self):
        self.sensors.track = 200
        required_course = 180
        for_three_seconds = 3

        self.helm.steer_course(required_course,for_three_seconds)

        self.servo.set_position.assert_has_calls([call(-10),call(-10),call(-10)])
        self.timer.wait_for.assert_has_calls([call(1),call(1),call(1)])
