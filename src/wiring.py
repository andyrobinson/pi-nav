import logging
import serial

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
from helm import Helm
from course_steerer import CourseSteerer
from events import Exchange
from event_source import EventSource
from timeshift import TimeShift
from i2c import I2C
from windsensor import WindSensor

LOGGING_FORMAT = '%(asctime)s,%(levelname)s,%(message)s'
APPLICATION_NAME = 'waypoint_follower'
SERVO_PORT = '/dev/ttyACM0'
RUDDER_SERVO_CHANNEL = 0
RUDDER_MIN_PULSE = 1500 - 340
RUDDER_MAX_PULSE = 1500 + 340
RUDDER_MIN_ANGLE = -30
RUDDER_MAX_ANGLE = 30
WINDSENSOR_I2C_ADDRESS = 0x40

class Wiring():
    def __init__(self,gps=False,servo_port=SERVO_PORT):
        self.injected_gps = gps
        self.windsensor = WindSensor(I2C(WINDSENSOR_I2C_ADDRESS))

        self.globe = Globe()
        self.timer = Timer()
        self.tracker = Tracker(self._rotating_logger("track"),self.gps,self.timer)
        self.application_logger = self._rotating_logger(APPLICATION_NAME)
        self.exchange = Exchange(self.application_logger)
        self.timeshift = TimeShift(self.exchange,self.timer.time)
        self.event_source = EventSource(self.exchange,self.timer,self.application_logger)

        self.sensors = Sensors(self.gps,self.windsensor,self.exchange,CONFIG['sensors'])
        self.gps_console_writer = GpsConsoleWriter(self.gps)
        self.rudder_servo = Servo(serial.Serial(servo_port),RUDDER_SERVO_CHANNEL,RUDDER_MIN_PULSE,RUDDER_MIN_ANGLE,RUDDER_MAX_PULSE,RUDDER_MAX_ANGLE)
        self.helm = Helm(self.sensors,self.rudder_servo,self.application_logger,CONFIG['helm'])
        self.course_steerer = CourseSteerer(self.sensors,self.helm,self.timer,CONFIG['course steerer'])
        self.navigator = Navigator(self.sensors,self.globe,self.exchange,self.application_logger,CONFIG['navigator'])

    def _rotating_logger(self,appname):
        logHandler = TimedRotatingFileHandler("/var/log/pi-nav/" + appname,when="midnight",backupCount=30)
        logHandler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        logger = logging.getLogger(appname)
        logger.addHandler( logHandler )
        logger.setLevel( logging.INFO )
        return logger

    @property
    def gps(self):
        if not self.injected_gps:
            self._gps = GpsReader()
            self._gps.setDaemon(True)
            self._gps.start()
        return self.injected_gps

    def showgps(self):
        try:
            self.timer.call(self.gps_console_writer.write).every(5)
        except (KeyboardInterrupt, SystemExit):
            self.gps.running = False
            self.gps.join()

    def follow(self,waypoints):
        self.rudder_servo.set_position(0)
        self.follower = Follower(self.exchange,self.navigator,waypoints,self.application_logger)
        self.event_source.start()
