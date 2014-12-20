from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call
from servo import Servo

class TestServo(unittest.TestCase):

    def setUp(self):
        self.serial = Mock()
        self.channel,self.min_pulse,self.min_angle,self.max_pulse,self.max_angle = 1,500,-90,2500,90
        self.servo = Servo(self.serial,self.channel,self.min_pulse,self.min_angle,self.max_pulse,self.max_angle)

    def position_bytes_from_angle(self,angle, shift=7, mask=0x7f):
        arc = self.max_angle - self.min_angle
        zeroed_angle = angle - self.min_angle
        pulse_range = self.max_pulse-self.min_pulse
        position = int(((float(zeroed_angle)/arc) * pulse_range) + self.min_pulse) * 4
        position_low = chr(position & mask)
        position_high = chr((position >> shift) & mask)
        return position_low,position_high

    def test_should_initialise(self):
        servo = self.servo
        self.assertEqual(servo.serial,self.serial)
        self.assertEqual(servo.channel,self.channel)
        self.assertEqual(servo.min_pulse,self.min_pulse)
        self.assertEqual(servo.min_angle,self.min_angle)

    def test_should_set_the_angle_using_the_serial_object_provided(self):
        self.servo.set_position(10)
        position_low,position_high = self.position_bytes_from_angle(10)
        set_position_command = chr(0xaa) + chr(0x0c) + chr(0x04)
        self.serial.write.assert_called_with(set_position_command + chr(self.channel) + position_low + position_high)

    def test_should_issue_the_get_position_command_then_read_the_8bit_results(self):
        expected_position = -15
        position_low,position_high = self.position_bytes_from_angle(expected_position,8,0xff)
        self.serial.read.side_effect = [position_low,position_high]
        get_position_command = chr(0xaa) + chr(0x0c) + chr(0x10)
        position = int(round(self.servo.get_position()))

        self.assertEqual(expected_position,position)
        self.serial.write.assert_called_with(get_position_command + chr(self.channel))

    def test_should_get_errors(self):
        expected_errors = (50,51)
        self.serial.read.side_effect = map(chr,expected_errors)
        get_errors_command = chr(0xaa) + chr(0x0c) + chr(0x21)

        errors = self.servo.get_errors()

        self.assertEqual(expected_errors, errors)
        self.serial.write.assert_called_with(get_errors_command)
