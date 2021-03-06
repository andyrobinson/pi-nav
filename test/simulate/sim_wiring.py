from test import setup_test
setup_test.setup_test()
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
from steerer import Steerer
from helm import Helm
from course_steerer import CourseSteerer
from events import Exchange
from event_source import EventSource
from timeshift import TimeShift

from simulated_vehicle import SimulatedVehicle
from simulated_gps import SimulatedGPS
from fake_sensors import FakeSensors

from test.utils import stub_gps

LOGGING_FORMAT = '%(asctime)s,%(levelname)s,%(message)s'

CHORLTON = Waypoint(Position(53.4407973,-2.272291),5)
MANCHESTER = Waypoint(Position(53.479324,-2.2484851),5)
LOWRY = Waypoint(Position(53.4708,-2.29607),5)
ALTRINCHAM = Waypoint(Position(53.39018,-2.3509),5)
MANCHESTER_TOUR = [CHORLTON, MANCHESTER, LOWRY, ALTRINCHAM, CHORLTON]
TEN_METRE_SQUARE = [Waypoint(Position(10,10),1),
                    Waypoint(Position(10.0001,10),1),
                    Waypoint(Position(10.0001,10.0001),1),
                    Waypoint(Position(10,10.0001),1),
                    Waypoint(Position(10,10),1)]

TWENTY_METRE_HOURGLASS = [Waypoint(Position(10,10),1),
                    Waypoint(Position(10.0002,10.0002),1),
                    Waypoint(Position(10,10.0002),1),
                    Waypoint(Position(10.0002,10),1),
                    Waypoint(Position(10,10),1)]

class SimWiring():
    def __init__(self):
        self.globe = Globe()
        self.console_logger = self._console_logger()
        self.exchange = Exchange(self.console_logger)
        self.gps = SimulatedGPS(CHORLTON.position,0,0.1)
        self.vehicle = SimulatedVehicle(self.gps, self.globe,self.console_logger,single_step=False)
        self.timeshift = TimeShift(self.exchange,self.vehicle.timer.time)
        self.event_source = EventSource(self.exchange,self.vehicle.timer,self.console_logger,CONFIG['event source'])
        self.sensors = Sensors(self.vehicle.gps, self.vehicle.windsensor,self.vehicle.compass,self.vehicle.timer.time,self.exchange,self.console_logger,CONFIG['sensors'])
        self.steerer = Steerer(self.vehicle.rudder,self.console_logger,CONFIG['steerer'])
        self.helm = Helm(self.exchange, self.sensors, self.steerer, self.console_logger, CONFIG['helm'])
        self.course_steerer = CourseSteerer(self.sensors,self.helm,self.vehicle.timer, CONFIG['course steerer'])
        self.navigator_simulator = Navigator(self.sensors,self.globe,self.exchange,self.console_logger,CONFIG['navigator'])

        self.tracking_timer = Timer()
        self.tracker_simulator = Tracker(self.console_logger,self.sensors,self.tracking_timer)

    def _console_logger(self):
        logging.basicConfig(format=LOGGING_FORMAT, level=CONFIG['wiring']['logging level'])
        return logging.getLogger("simulate")

    def _follower(self,waypoints):
        self.follower_simulator =  Follower(self.exchange,waypoints,self.console_logger)
        return self.follower_simulator

    def follow(self,waypoints):
        self.gps.set_position(waypoints[0].position,0,0.8,True)
        self.vehicle.position = waypoints[0].position
        self.follower_simulator =  self._follower(waypoints)
        self.event_source.start()
