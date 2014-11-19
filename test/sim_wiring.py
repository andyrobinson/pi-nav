from setup_test import setup_test
setup_test()
import logging
from position import Position
from waypoint import Waypoint
from navigator import Navigator
from follower import Follower
from sensors import Sensors
from globe import Globe
from timer import Timer
from track import Tracker

from simulate.fake_vehicle import FakeVehicle
from simulate.stub_gps import StubGPS

LOGGING_FORMAT = '%(asctime)s,%(levelname)s,%(message)s'

CHORLTON = Waypoint(Position(53.4407973,-2.272291),5)
MANCHESTER = Waypoint(Position(53.479324,-2.2484851),5)
LOWRY = Waypoint(Position(53.4708,-2.29607),5)
ALTRINCHAM = Waypoint(Position(53.39018,-2.3509),5)

class SimWiring():
    def __init__(self):
        self._gps = False
        self._globe = Globe()
        self._console_logger = False
        
    def console_logger(self):
        if not self._console_logger:
            logging.basicConfig(format=LOGGING_FORMAT, level=logging.DEBUG)
            self._console_logger = logging.getLogger("simulate")
        return self._console_logger
            
    def globe(self):
        return self._globe

    def navigator_simulator(self):
        fake_vehicle = FakeVehicle(CHORLTON.position, self.globe(),self.console_logger())
        return Navigator(Sensors(fake_vehicle.gps),fake_vehicle,self.globe(),self.console_logger())

    def follower_simulator(self):
        return Follower(self.navigator_simulator(),self.console_logger())
    
    def manchester_tour(self):
        return [CHORLTON, MANCHESTER, LOWRY, ALTRINCHAM, CHORLTON]
        
    def tracker_simulator(self):
        gps = StubGPS()
        return Tracker(self.console_logger(),gps,self.timer())

    def timer(self):
        return Timer()
        
