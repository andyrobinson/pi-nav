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
from config import CONFIG

from simulate.fake_vehicle import FakeVehicle
from simulate.fake_vehicle_gps import FakeVehicleGPS

from simulate.stub_gps import StubGPS

LOGGING_FORMAT = '%(asctime)s,%(levelname)s,%(message)s'

CHORLTON = Waypoint(Position(53.4407973,-2.272291),5)
MANCHESTER = Waypoint(Position(53.479324,-2.2484851),5)
LOWRY = Waypoint(Position(53.4708,-2.29607),5)
ALTRINCHAM = Waypoint(Position(53.39018,-2.3509),5)

class SimWiring():
    def __init__(self):
        self.globe = Globe()
        self.timer = Timer()
        self.console_logger = self._console_logger()
        self.navigator_simulator = self._navigator_simulator()
        self.follower_simulator =  Follower(self.navigator_simulator,self.console_logger)
        self.manchester_tour = [CHORLTON, MANCHESTER, LOWRY, ALTRINCHAM, CHORLTON]
        self.tracker_simulator = Tracker(self.console_logger,StubGPS(),self.timer)

    def _console_logger(self):
        logging.basicConfig(format=LOGGING_FORMAT, level=logging.DEBUG)
        return logging.getLogger("simulate")

    def _navigator_simulator(self):
        fake_gps = FakeVehicleGPS(CHORLTON.position,0,0.1,False)
        fake_vehicle = FakeVehicle(fake_gps, self.globe,self.console_logger)
        return Navigator(Sensors(fake_vehicle.gps),fake_vehicle,self.globe,self.console_logger,CONFIG['navigator'])
