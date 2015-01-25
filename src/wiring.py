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

LOGGING_FORMAT = '%(asctime)s,%(levelname)s,%(message)s'
APPLICATION_NAME = 'waypoint_follower'
SERVO_PORT = '/dev/ttyACM0'
RUDDER_SERVO_CHANNEL = 0
RUDDER_MIN_PULSE = 1500 - 340
RUDDER_MAX_PULSE = 1500 + 340
RUDDER_MIN_ANGLE = -30
RUDDER_MAX_ANGLE = 30

class Wiring():
    def __init__(self,gps=False,servo_port=SERVO_PORT):
        self._gps = gps

        self.globe = Globe()
        self.timer = Timer()
        self.tracker = Tracker(self._rotating_logger("track"),self.gps,self.timer)
        self.application_logger = self._rotating_logger(APPLICATION_NAME)
        self.sensors = Sensors(self.gps)
        self.gps_console_writer = GpsConsoleWriter(self.gps)
        self.rudder_servo = Servo(serial.Serial(servo_port),RUDDER_SERVO_CHANNEL,RUDDER_MIN_PULSE,RUDDER_MIN_ANGLE,RUDDER_MAX_PULSE,RUDDER_MAX_ANGLE)
        self.helm = Helm(self.sensors,self.rudder_servo,self.application_logger,CONFIG['helm'])
        self.course_steerer = CourseSteerer(self.sensors,self.helm,self.timer,CONFIG['course steerer'])
        self.navigator = Navigator(self.sensors,self.course_steerer,self.globe,self.application_logger,CONFIG['navigator'])
        self.follower = Follower(self.navigator,self.application_logger)

    def _rotating_logger(self,appname):
        logHandler = TimedRotatingFileHandler("/var/log/pi-nav/" + appname,when="midnight",backupCount=30)
        logHandler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        logger = logging.getLogger(appname)
        logger.addHandler( logHandler )
        logger.setLevel( logging.INFO )
        return logger

    @property        
    def gps(self):
        if not self._gps:
            self._gps = GpsReader()
        return self._gps

    def showgps(self):
        try:
            self.timer().call(self.gps_console_writer.write).every(5)
        except (KeyboardInterrupt, SystemExit):
            self.gps.running = False
            self.gps.join()

    def follow(self,waypoints):
        self.rudder_servo.set_position(0)
        self.follower.follow_route(waypoints)
