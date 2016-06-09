from bearing import to_360
from math import sqrt,cos,radians,degrees,copysign
import sys

INITIAL_SPEED_IN_MS = 0.8
TIME_INCREMENT_IN_SEC = 5
TURN_FACTOR = 30
MIN_TURN_RADIUS = 1

class SimulatedCompass():
    def __init__(self):
        self._bearing = 0

    def bearing(self):
        return self._bearing

    def set_bearing(self,new_bearing):
        self._bearing = new_bearing

class SimulatedWindSensor():
    def __init__(self):
        self._angle = 0

    def angle(self):
        return self._angle

    def set_angle(self,new_angle):
        self._angle = new_angle

class SimulatedRudder():
    def __init__(self):
        self.angle = 0

    def set_position(self,angle):
        self.angle = angle

class SimulatedTimer():

    def __init__(self,callback):
        self.callback = callback
        self.fake_time = 0

    def wait_for(self,seconds):
        self.fake_time += seconds
        self.callback(seconds)

    def time(self):
        return self.fake_time

    def tick(self):
        self.fake_time += 0.2

class SimulatedVehicle():
    def __init__(self,gps, globe, logger, single_step = False):
        self.single_step = single_step
        self.gps = gps
        self.globe = globe
        self.logger = logger
        self.speed = INITIAL_SPEED_IN_MS
        self.gps.speed = INITIAL_SPEED_IN_MS
        self.rudder = SimulatedRudder()
        self.timer = SimulatedTimer(self.move)
        self.windsensor = SimulatedWindSensor()
        self.compass = SimulatedCompass()
        self.position = self.gps.position
        self.track = self.gps.track

    def move(self,seconds):
        distance = self.speed * seconds
        if abs(self.rudder.angle) <=1:
            self._move_straight(distance)
        else:
            self._turn(distance)

        self.logger.debug("Vehicle at: {:+f},{:+f}, rudder: {:f}, track: {:f}"
                          .format(self.position.latitude, self.position.longitude, self.rudder.angle, self.track))
        self.logger.debug("GPS reports {:+f},{:+f}, track: {:f}"
                          .format(self.gps.position.latitude, self.gps.position.longitude, self.gps.track))

    def _move_straight(self,distance):
        new_position = self.globe.new_position(self.position,self.track,distance)
        self._set_position(new_position,self.track)

    def _turn(self,distance):
        turn_radius = self._turn_radius(self.rudder.angle)
        track_delta = - copysign(self._track_delta(distance, turn_radius),self.rudder.angle)
        new_track = to_360(self.track + track_delta)
        move_bearing = self.track + self._straightline_angle(track_delta)
        move_distance = self._straightline_distance(turn_radius,track_delta)
        new_position = self.globe.new_position(self.position,move_bearing,move_distance)
        self._set_position(new_position,new_track)

    def _set_position(self,position,track):
        position.lat_error = 3
        position.long_error = 3

        if self.single_step:
            sys.stdout.write('Enter to continue:')
            x = sys.stdin.readline()
        self.position = position
        self.track = track
        self.gps.set_position(position, track, self.speed)

    def _straightline_distance(self,radius,angle_in_deg):
        return radius * sqrt(2 - 2 * cos(radians(angle_in_deg)))

    def _straightline_angle(self,angle):
        return float(angle) / 2

    def _turn_radius(self,rudder_angle_deg):
        return TURN_FACTOR/abs(float(rudder_angle_deg)) + MIN_TURN_RADIUS

    def _track_delta(self,distance,radius):
        return degrees(float(distance)/radius)
