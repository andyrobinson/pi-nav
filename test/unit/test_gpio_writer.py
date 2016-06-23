from setup_test import setup_test
setup_test()
import unittest
from mock import Mock,call

from gpio_writer import GpioWriter

class TestGpioWriter(unittest.TestCase):

    def test_should_set_the_mode_on_the_first_command(self):
        mockOs = Mock()
        gpio_writer = GpioWriter(10,mockOs)
        gpio_writer.high()

        mockOs.system.assert_has_calls([call("gpio -g mode 10 out"),call("gpio -g write 10 1")])

    def test_should_not_set_the_mode_on_the_second_command(self):
        mockOs = Mock()
        gpio_writer = GpioWriter(10,mockOs)
        gpio_writer.high()
        mockOs.reset_mock()
        gpio_writer.high()

        mockOs.system.assert_called_once_with("gpio -g write 10 1")

    def test_should_set_the_port_high(self):
        mockOs = Mock()
        gpio_writer = GpioWriter(10,mockOs)
        gpio_writer.high()

        mockOs.system.assert_has_calls([call("gpio -g mode 10 out"),call("gpio -g write 10 1")])

    def test_should_set_the_port_low(self):
        mockOs = Mock()
        gpio_writer = GpioWriter(10,mockOs)
        gpio_writer.low()

        mockOs.system.assert_has_calls([call("gpio -g mode 10 out"),call("gpio -g write 10 0")])
