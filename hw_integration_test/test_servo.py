from setup_test import setup_test
setup_test()

from test_utils import percentage_diff

import unittest
import time

import serial
from servo import Servo

class TestServo(unittest.TestCase):
    
    def set_and_read_position(self,servo,position):
        servo.set_position(position)
        time.sleep(3)
        return servo.get_position()

    def test_should_be_able_to_move_servo_and_read_position(self):
        serial_port0 = serial.Serial('/dev/ttyACM0')
        servo = Servo(serial_port0,0,500,-90,2500,90)

        for position in [-90,-45,0,45,90,0]:
            self.assertLess(percentage_diff(self.set_and_read_position(servo,position),position),500)

    def test_for_errors(self):
        pass
