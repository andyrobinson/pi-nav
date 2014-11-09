import traceback
from position import Position
from nan import NaN,isNaN
from fake_vehicle_gps import FakeVehicleGPS

SPEED = 10

class FakeVehicle():
    def __init__(self,initial_position, globe, logger):
        self.position = initial_position
        self.gps = FakeVehicleGPS(initial_position,0,0)
        self.globe = globe
        self.logger = logger
    
    def steer(self,requested_bearing):
        if isNaN(requested_bearing):
           raise RuntimeError("Steer called without a valid bearing")

        new_position = self.globe.new_position(self.position,requested_bearing,SPEED)
        new_position.lat_error = 3
        new_position.long_error = 3

        self.logger.debug("Vehicle at: {:+f},{:+f}, stack size: {:d}".format(new_position.latitude, new_position.longitude, len(traceback.format_stack())))
        self.position = new_position
        self.gps.set_position(new_position,requested_bearing,SPEED)


