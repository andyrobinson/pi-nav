from setup_test import setup_test
setup_test()

from test_utils import percentage_diff

import unittest
import time

import serial
from servo import Servo

class TestServo(unittest.TestCase):
    
    def set_and_read_position(self,position):
        self.servo.set_position(position)
        time.sleep(1)
        return self.servo.get_position()

    def setUp(self):
        serial_port0 = serial.Serial('/dev/ttyACM0')
        self.servo = Servo(serial_port0,0,500,-90,2500,90)

    def test_should_be_able_to_move_servo_and_read_position(self):

        for position in [-90,-45,5,45,90]:
            self.assertLess(percentage_diff(self.set_and_read_position(position),position),1)

    def test_for_errors(self):
        a,b = self.servo.get_errors
        self.assertEqual(a,0)
        self.assertEqual(b,0)
