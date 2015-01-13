import random
from position import Position
from nan import NaN

class FakeVehicleGPS():
    def __init__(self, position, track, speed, reliable = False):
        self._set_position(position,track,speed)
        self.lost_position = False
        self.reliable = reliable
        
    def set_position(self,position,track,speed, reliable = False):
        rand = random.randrange(1,101)
        if self.reliable or reliable:
            rand = 70
        if rand > 50:
            self.lost_position = False

        if rand < 10:
            self.lost_position = True

        if self.lost_position:
            print '********* GPS LOST SIGNAL *********'
            self._no_signal()
        else:
            if rand > 80:
                self._set_position_no_error(position,track,speed)
            else:
                self._set_position(position,track,speed)

    def _set_position_no_error(self,position,track,speed):
        self.hasfix = True
        self.position = Position(position.latitude, position.longitude, NaN,NaN)
        self.track = track
        self.speed = speed
        self.time = 10
        self.speed_error = NaN
        self.track_error = NaN

    def _set_position(self,position,track,speed):
        self.hasfix = True
        self.position = position
        self.track = track
        self.speed = speed
        self.time = 10
        self.speed_error =1
        self.track_error = 2

    def _no_signal(self):
        self.hasfix = False
        self.position = Position(NaN,NaN,NaN,NaN)
        self.track = NaN
        self.speed = NaN
        self.time = NaN
        self.speed_error = NaN
        self.track_error = NaN