import logging
from logging.handlers import TimedRotatingFileHandler
from track import Tracker
from fake_gps import FakeGPS
from timed_callback import TimedCallback
from gps_reader import GpsReader
from gps_console_writer import GpsConsoleWriter
from globe import Globe
from position import Position
from waypoint import Waypoint
from navigator import Navigator
from follower import Follower
from sensors import Sensors

LOGGING_FORMAT = '%(asctime)s,%(levelname)s,%(message)s'

class Wiring():
    def __init__(self):
        self._gps = False
        self._globe = Globe()
        self._console_logger = False
        
    def application_logger(self,appname):
        logHandler = TimedRotatingFileHandler("/var/log/pi-nav/" + appname,when="midnight",backupCount=30)
        logHandler.setFormatter(logging.Formatter(LOGGING_FORMAT))
        logger = logging.getLogger(appname)
        logger.addHandler( logHandler )
        logger.setLevel( logging.INFO )
        return logger

    def tracker(self):
        return Tracker(self.application_logger("track"),self.gps(),self.timed_callback())
        
    def gps(self):
        if not self._gps:
            self._gps = GpsReader()
            self._gps.start()
        return self._gps
    
    def timed_callback(self):
        return TimedCallback()
        
    def tracker_simulator(self):
        gps = FakeGPS()
        return Tracker(self.console_logger(),gps,self.timed_callback())

    def gps_console_writer(self):
        return GpsConsoleWriter(self.gps())
        
    def showgps(self):
        try:
            self.timed_callback().call(self.gps_console_writer().write).every(5)
        except (KeyboardInterrupt, SystemExit):
            self.gps().running = False
            self.gps().join() 

    def globe(self):
        return self._globe
        
        