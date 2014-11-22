import traceback
from position import Position
from nan import NaN,isNaN
from fake_vehicle_gps import FakeVehicleGPS

SPEED_IN_MS = 5
TIME_INCREMENT_IN_SEC = 5

class FakeVehicle():
    def __init__(self,gps, globe, logger):
        self.position = gps.position
        self.gps = gps
        self.globe = globe
        self.logger = logger
        self.speed = SPEED_IN_MS
        self.gps.speed = SPEED_IN_MS
    
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


