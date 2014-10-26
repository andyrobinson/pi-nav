import traceback
import random
from position import Position
from nan import NaN,isNaN

SPEED = 10
    
class VehicleGPS():
    def __init__(self, position, track, speed):
        self.set_position(position,track,speed)
        
    def set_position(self,position,track,speed):
        self.hasfix = True
        self.position = position
        self.track = track
        self.speed = speed
        self.time = 10
        self.speed_error =1
        self.track_error = 2

    def no_signal(self):
        self.hasfix = False
        self.position = Position(NaN,NaN,NaN,NaN)
        self.track = NaN
        self.speed = NaN
        self.time = NaN
        self.speed_error = NaN
        self.track_error = NaN

class FakeVehicle():
    def __init__(self,initial_position, globe, logger):
        self.position = initial_position
        self.gps = VehicleGPS(initial_position,0,0)
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

        if random.randrange(1,101) <  10:
            print '********* GPS LOST SIGNAL *********'
            self.gps.no_signal()
        else:
            self.gps.set_position(new_position,requested_bearing,SPEED)

