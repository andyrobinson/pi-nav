import logging
import serial

from logging.handlers import TimedRotatingFileHandler
from track import Tracker
from timer import Timer
from gps_reader import GpsReader
from gps_console_writer import GpsConsoleWriter
from globe import Globe
from position import Position
from waypoint import Waypoint
from navigator import Navigator
from follower import Follower
from sensors import Sensors
from config import CONFIG
from servo import Servo
from helm import Helm

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
        self._servo_port = servo_port
        self._sensors = False
        self._rudder_servo = False
        self._navigator = False

    def _rotating_logger(self,appname):
        logHandler = TimedRotatingFileHandler("/var/log/pi-nav/" + appname,when="midnight",backupCount=30)
        logHandler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        logger = logging.getLogger(appname)
        logger.addHandler( logHandler )
        logger.setLevel( logging.INFO )
        return logger

    @property
    def application_logger(self):
        return self._rotating_logger(APPLICATION_NAME)

    @property        
    def gps(self):
        if not self._gps:
            self._gps = GpsReader()
        return self._gps

    def tracker(self):
        return Tracker(self._rotating_logger("track"),self.gps,self.timer())

    
    def sensors(self):
        if not self._sensors:
            self._sensors = Sensors(self.gps)
        return self._sensors

    def timer(self):
        return Timer()
        
    def gps_console_writer(self):
        return GpsConsoleWriter(self.gps)
        
    def showgps(self):
        try:
            self.timer().call(self.gps_console_writer().write).every(5)
        except (KeyboardInterrupt, SystemExit):
            self.gps.running = False
            self.gps.join() 

    def rudder_servo(self):
        if not self._rudder_servo:
            serial_port = serial.Serial(self._servo_port)
            self._rudder_servo = Servo(serial_port,RUDDER_SERVO_CHANNEL,RUDDER_MIN_PULSE,RUDDER_MIN_ANGLE,RUDDER_MAX_PULSE,RUDDER_MAX_ANGLE)
        return self._rudder_servo

    def helm(self):
        return Helm(self.sensors(),self.rudder_servo(),self.timer(),self.application_logger,CONFIG['helm'])

    def follower(self):
        return Follower(self.navigator(),self.application_logger)

    def navigator(self):
        if not self._navigator:
            self._navigator = Navigator(self.sensors(),self.helm(),self.globe,self.application_logger,CONFIG['navigator'])
        return self._navigator