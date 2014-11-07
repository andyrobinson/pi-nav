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
from fake_vehicle import FakeVehicle
from navigator import Navigator
from follower import Follower
from sensors import Sensors

LOGGING_FORMAT = '%(asctime)s,%(levelname)s,%(message)s'

CHORLTON = Waypoint(Position(53.4407973,-2.272291),5)
MANCHESTER = Waypoint(Position(53.479324,-2.2484851),5)
LOWRY = Waypoint(Position(53.4708,-2.29607),5)
ALTRINCHAM = Waypoint(Position(53.39018,-2.3509),5)

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

    def console_logger(self):
        if not self._console_logger:
            logging.basicConfig(format=LOGGING_FORMAT, level=logging.DEBUG)
            self._console_logger = logging.getLogger("simulate")
        return self._console_logger
        
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

    def navigator_simulator(self):
        fake_vehicle = FakeVehicle(CHORLTON.position, self.globe(),self.console_logger())
        return Navigator(Sensors(fake_vehicle.gps),fake_vehicle,self.globe(),self.console_logger())

    def follower_simulator(self):
        return Follower(self.navigator_simulator(),self.console_logger())
    
    def manchester_tour(self):
        return [CHORLTON, MANCHESTER, LOWRY, ALTRINCHAM, CHORLTON]
        
        