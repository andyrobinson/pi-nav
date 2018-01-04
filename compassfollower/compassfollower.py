import logging
import serial
import os
import datetime
import time
from math import copysign

from config import CONFIG
from servo import Servo
from i2c import I2C
from compass import Compass
from bearing import angle_between

SERVO_PORT = '/dev/ttyACM0'
RUDDER_SERVO_CHANNEL = 0
RUDDER_MIN_PULSE = 1500 - 680
RUDDER_MAX_PULSE = 1500 + 680
RUDDER_MIN_ANGLE = -60
RUDDER_MAX_ANGLE =  60
COMPASS_I2C_ADDRESS = 0x1E
ACCELEROMETER_I2C_ADDRESS = 0x19
TARGET_BEARING = 270.0

class CompassFollower():
    def __init__(self,gps=False,servo_port=SERVO_PORT):
        # devices
        self.compass = Compass(I2C(COMPASS_I2C_ADDRESS),I2C(ACCELEROMETER_I2C_ADDRESS))
        self.rudder_servo = Servo(serial.Serial(servo_port),RUDDER_SERVO_CHANNEL,RUDDER_MIN_PULSE,RUDDER_MIN_ANGLE,RUDDER_MAX_PULSE,RUDDER_MAX_ANGLE)

	try:
           while True:
              current_bearing = self.compass.bearing
              difference = angle_between(TARGET_BEARING, current_bearing)

              # for definite rudder deflection at low angles for difference:
              # scaled_diff = max(5, abs(difference/3))
              # rudder_angle = copysign(scaled_diff,difference)

              # for tolerance of small differences
              rudder_angle = difference/3 if abs(difference) > 5 else 0

              self.rudder_servo.set_position(rudder_angle)
              print('Current bearing {:+.1f}, target {:+.1f}, rudder {:+.1f}'.format(current_bearing, TARGET_BEARING, rudder_angle))

              # smooth response with a sleep time of less than 100ms ?
              time.sleep(0.1)
   
        except (KeyboardInterrupt, SystemExit):
           quit()

