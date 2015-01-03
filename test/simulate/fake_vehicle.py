import traceback
from position import Position
from nan import NaN,isNaN
from fake_vehicle_gps import FakeVehicleGPS

INITIAL_SPEED_IN_MS = 0.5
TIME_INCREMENT_IN_SEC = 5
TURN_FACTOR = 30
MIN_TURN_RADIUS = 1

class FakeRudder():
    def set_position(self,angle):
        self.angle = angle

class FakeTimer():
    def __init__(self,callback):
        self.callback = callback

    def wait_for(self,seconds):
        self.callback(seconds)

class FakeVehicle():
    def __init__(self,gps, globe, logger):
        self.position = gps.position
        self.gps = gps
        self.globe = globe
        self.logger = logger
        self.speed = INITIAL_SPEED_IN_MS
        self.gps.speed = INITIAL_SPEED_IN_MS
        self.rudder = FakeRudder()
        self.timer = FakeTimer(self.move)
    
    def steer_course(self,requested_bearing,for_seconds):
        if isNaN(requested_bearing):
           raise RuntimeError("Steer called without a valid bearing")

        seconds_steered  = 0
        while seconds_steered < for_seconds:
            new_position = self.globe.new_position(self.position,requested_bearing,self.speed * TIME_INCREMENT_IN_SEC)
            new_position.lat_error = 3
            new_position.long_error = 3

            self.logger.debug("Vehicle at: {:+f},{:+f}, stack size: {:d}".format(new_position.latitude, new_position.longitude, len(traceback.format_stack())))
            self.position = new_position
            self.gps.set_position(new_position,requested_bearing,self.speed)
            seconds_steered = seconds_steered + TIME_INCREMENT_IN_SEC

    def move(self,seconds):
        distance = self.speed * seconds        
        new_position = self.globe.new_position(self.position,self.gps.track,distance)
        new_position.lat_error = 3
        new_position.long_error = 3
        self.gps.set_position(new_position,self.gps.track,self.speed)

        self.logger.debug("Vehicle at: {:+f},{:+f}, stack size: {:d}".format(new_position.latitude, new_position.longitude, len(traceback.format_stack())))
