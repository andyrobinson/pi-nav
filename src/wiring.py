import logging
import serial
import os

from logging.handlers import TimedRotatingFileHandler
from track import Tracker
from timer import Timer
from gps_reader import GpsReader
from gps_console_writer import GpsConsoleWriter
from globe import Globe
from navigator import Navigator
from follower import Follower
from sensors import Sensors
from config import CONFIG
from servo import Servo
from steerer import Steerer
from helm import Helm
from course_steerer import CourseSteerer
from events import Exchange
from event_source import EventSource
from timeshift import TimeShift
from i2c import I2C
from windsensor import WindSensor
from compass import Compass
from gpio_writer import GpioWriter
from self_test import SelfTest

LOGGING_FORMAT = '%(asctime)s,%(levelname)s,%(message)s'
APPLICATION_NAME = 'waypoint_follower'
SERVO_PORT = '/dev/ttyACM0'
RUDDER_SERVO_CHANNEL = 0
RUDDER_MIN_PULSE = 1500 - 340
RUDDER_MAX_PULSE = 1500 + 340
RUDDER_MIN_ANGLE = -30
RUDDER_MAX_ANGLE = 30
WINDSENSOR_I2C_ADDRESS = 0x40
COMPASS_I2C_ADDRESS = 0x1E
ACCELEROMETER_I2C_ADDRESS = 0x19

class Wiring():
    def __init__(self,gps=False,servo_port=SERVO_PORT):
        # devices
        self._gps = gps
        self.windsensor = WindSensor(I2C(WINDSENSOR_I2C_ADDRESS))
        self.compass = Compass(I2C(COMPASS_I2C_ADDRESS),I2C(ACCELEROMETER_I2C_ADDRESS))
        self.red_led = GpioWriter(17,os)
        self.green_led = GpioWriter(18,os)

        # Navigation
        self.globe = Globe()
        self.timer = Timer()
        self.application_logger = self._rotating_logger(APPLICATION_NAME)
        self.position_logger = self._rotating_logger("position")
        self.exchange = Exchange(self.application_logger)
        self.timeshift = TimeShift(self.exchange,self.timer.time)
        self.event_source = EventSource(self.exchange,self.timer,self.application_logger,CONFIG['event source'])

        self.sensors = Sensors(self.gps,self.windsensor,self.compass,self.timer.time,self.exchange,self.position_logger,CONFIG['sensors'])
        self.gps_console_writer = GpsConsoleWriter(self.gps)
        self.rudder_servo = Servo(serial.Serial(servo_port),RUDDER_SERVO_CHANNEL,RUDDER_MIN_PULSE,RUDDER_MIN_ANGLE,RUDDER_MAX_PULSE,RUDDER_MAX_ANGLE)
        self.steerer = Steerer(self.rudder_servo,self.application_logger,CONFIG['steerer'])
        self.helm = Helm(self.exchange,self.sensors,self.steerer,self.application_logger,CONFIG)
        self.course_steerer = CourseSteerer(self.sensors,self.helm,self.timer,CONFIG['course steerer'])
        self.navigator = Navigator(self.sensors,self.globe,self.exchange,self.application_logger,CONFIG['navigator'])
        self.self_test = SelfTest(self.red_led,self.green_led,self.timer,self.rudder_servo,RUDDER_MIN_ANGLE,RUDDER_MAX_ANGLE)

        # Tracking
        self.tracking_logger = self._rotating_logger("track")
        self.tracking_sensors = Sensors(self.gps,self.windsensor,self.compass,self.timer.time,self.exchange,self.tracking_logger,CONFIG['sensors'])
        self.tracker = Tracker(self.tracking_logger,self.tracking_sensors,self.timer)

    def _rotating_logger(self,appname):
        logHandler = TimedRotatingFileHandler("/var/log/pi-nav/" + appname,when="midnight",backupCount=30)
        logHandler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        logger = logging.getLogger(appname)
        logger.addHandler( logHandler )
        logger.setLevel( logging.DEBUG )
        return logger

    @property
    def gps(self):
        if not self._gps:
            self._gps = GpsReader()
            self._gps.setDaemon(True)
            self._gps.start()
        return self._gps

    def showgps(self):
        try:
            self.timer.call(self.gps_console_writer.write).every(5)
        except (KeyboardInterrupt, SystemExit):
            self.gps.running = False
            self.gps.join()

    def follow(self,waypoints):
        self.self_test.run()
        self.rudder_servo.set_position(0)
        self.follower = Follower(self.exchange,waypoints,self.application_logger)
        self.event_source.start()

    def track(self):
        self.self_test.run()
        self.tracker.track(10)
