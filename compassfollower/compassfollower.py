import logging
import serial
import os
import datetime
import time

from config import CONFIG
from servo import Servo
from i2c import I2C
from compass import Compass

SERVO_PORT = '/dev/ttyACM0'
RUDDER_SERVO_CHANNEL = 0
RUDDER_MIN_PULSE = 1500 - 340
RUDDER_MAX_PULSE = 1500 + 340
RUDDER_MIN_ANGLE = -30
RUDDER_MAX_ANGLE = 30
COMPASS_I2C_ADDRESS = 0x1E
ACCELEROMETER_I2C_ADDRESS = 0x19

class CompassFollower():
    def __init__(self,gps=False,servo_port=SERVO_PORT):
        # devices
        self.compass = Compass(I2C(COMPASS_I2C_ADDRESS),I2C(ACCELEROMETER_I2C_ADDRESS))
        self.rudder_servo = Servo(serial.Serial(servo_port),RUDDER_SERVO_CHANNEL,RUDDER_MIN_PULSE,RUDDER_MIN_ANGLE,RUDDER_MAX_PULSE,RUDDER_MAX_ANGLE)

	try:
           while True:
              print("Doing something")
              time.sleep(0.5)
   
        except (KeyboardInterrupt, SystemExit):
           quit()

