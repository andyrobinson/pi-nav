from setup_test import setup_test
setup_test()
import unittest
from mock import Mock,call
from self_test import SelfTest
from wiring import RUDDER_MIN_ANGLE,RUDDER_MAX_ANGLE

class TestSelfTest(unittest.TestCase):

    def setUp(self):
        self.red_led,self.green_led,self.timer,self.rudder = Mock(),Mock(),Mock(),Mock()
        self.self_test = SelfTest(self.red_led,self.green_led,self.timer,self.rudder)

    def test_should_blink_red(self):
        self.self_test.run()

        self.assertEqual(1,self.red_led.high.call_count)
        self.assertEqual(1,self.red_led.low.call_count)
        self.timer.wait_for.assert_any_call(0.5)

    def test_should_waggle_the_rudder(self):
        self.rudder.reset_mock()
        self.self_test.run()

        self.rudder.set_position.assert_has_calls([call(RUDDER_MIN_ANGLE),call(RUDDER_MAX_ANGLE),call(0)])

    def test_should_signal_green_hopefully_at_the_end(self):
        self.self_test.run()

        self.assertEqual(1,self.green_led.high.call_count)
        self.assertEqual(1,self.green_led.low.call_count)
