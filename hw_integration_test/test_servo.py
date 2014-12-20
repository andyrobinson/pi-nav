from setup_test import setup_test
setup_test()

from test_utils import percentage_diff

import unittest
import time
import serial

from servo import Servo

class TestGps(unittest.TestCase):
    
    def set_and_read_position(self,servo,position):
        servo.set_position(position)
        time.sleep(0.1)
        return servo.get_position()

    def test_should_be_able_to_move_servo_and_read_position(self):
        serial = Serial.serial('/dev/ttyACM0')
        servo = Servo(serial,0,500,-90,2500,90)

        for position in [-90,-45,0,45,90,0]:
            self.assertLess(percentage_diff(set_and_read_position(position),position),0.1)

    def test_for_errors(self):
        pass