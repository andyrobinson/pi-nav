import traceback
from position import Position
from nan import NaN,isNaN
from fake_vehicle_gps import FakeVehicleGPS
from math import sqrt,cos,radians,degrees,copysign

INITIAL_SPEED_IN_MS = 0.8
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

            self.logger.debug("Vehicle at: {:+f},{:+f}, stack size: {:d}"
                              .format(new_position.latitude, new_position.longitude, len(traceback.format_stack())))
            self.position = new_position
            self.gps.set_position(new_position,requested_bearing,self.speed)
            seconds_steered = seconds_steered + TIME_INCREMENT_IN_SEC

    def move(self,seconds):
        distance = self.speed * seconds
        if (self.rudder.angle <=1):
            self._move_straight(distance)
        else:
            self._turn(distance)

        self.logger.debug("Vehicle at: {:+f},{:+f}, rudder: {:f}, track: {:f}"
                          .format(self.gps.position.latitude, self.gps.position.longitude, self.rudder.angle, self.gps.track))

    def _move_straight(self,distance):
        new_position = self.globe.new_position(self.gps.position,self.gps.track,distance)
        self._set_position(new_position,self.gps.track)

    def _turn(self,distance):
        turn_radius = self._turn_radius(self.rudder.angle)
        track_delta = - copysign(self._track_delta(distance, turn_radius),self.rudder.angle)
        new_track = self.gps.track + track_delta
        move_bearing = self.gps.track + self._straightline_angle(track_delta)
        move_distance = self._straightline_distance(turn_radius,track_delta)
        new_position = self.globe.new_position(self.gps.position,move_bearing,move_distance)
        self._set_position(new_position,new_track)

    def _set_position(self,position,track):
        position.lat_error = 3
        position.long_error = 3
        self.gps.set_position(position, track, self.speed)

    def _straightline_distance(self,radius,angle_in_deg):
        return radius * sqrt(2 - 2 * cos(radians(angle_in_deg)))

    def _straightline_angle(self,angle):
        return float(angle) / 2

    def _turn_radius(self,rudder_angle_deg):
        return TURN_FACTOR/abs(float(rudder_angle_deg)) + MIN_TURN_RADIUS

    def _track_delta(self,distance,radius):
        return degrees(float(distance)/radius)