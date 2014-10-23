import traceback

SPEED = 10

class VehicleGPS():
    def __init__(self, position, track, speed):
        self.hasfix = True
        self.position = position
        self.track = track
        self.speed = speed
        self.time = 10
        self.speed_error =1
        self.track_error = 2

class FakeVehicle():
    def __init__(self,initial_position, globe, logger):
        self.position = initial_position
        self.gps = VehicleGPS(initial_position,0,0)
        self.globe = globe
        self.logger = logger
    
    def steer(self,bearing):
        new_position = self.globe.new_position(self.gps.position,bearing,SPEED)
        new_position.lat_error = 3
        new_position.long_error = 3
        self.logger.debug("Vehicle at: {:+f},{:+f}, stack size: {:d}".format(new_position.latitude, new_position.longitude, len(traceback.format_stack())))
        self.gps.position = new_position
        self.gps.track = bearing
        self.gps.speed = SPEED
        