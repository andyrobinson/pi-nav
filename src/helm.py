from math import copysign
from nan import isNaN

WAIT_BETWEEN_STEERING_CORRECTION = 1

class Helm():
    def __init__(self,sensors,rudder_servo,timer,config):
        self.sensors = sensors
        self.rudder_servo = rudder_servo
        self._set_rudder_angle(0)
        self.config = config
        self.timer = timer

    def steer_course(self,requested_heading,for_seconds):
        remaining_seconds = for_seconds
        while remaining_seconds > 0:
            self.steer(requested_heading)
            self.timer.wait_for(WAIT_BETWEEN_STEERING_CORRECTION)
            remaining_seconds = remaining_seconds - WAIT_BETWEEN_STEERING_CORRECTION

    def steer(self,requested_heading):
        track = self.sensors.track

        if isNaN(track):
            self._set_rudder_angle(0)
        else:
            int_track = int(round(track))
            int_heading = int(round(requested_heading))
            turn_angle = self._turn_angle(int_track,int_heading)
            ignore_below = self.config['ignore deviation below']

            if abs(turn_angle) <  ignore_below and abs(self.rudder_angle) < ignore_below:
                return

            self._set_rudder_angle(self._calculate_rudder_angle(turn_angle))

    def _calculate_rudder_angle(self,turn_angle):
        unsigned_rudder_angle = min(self.config['full deflection'],int(abs(turn_angle)/2))
        return int(copysign(unsigned_rudder_angle,turn_angle))

    def _set_rudder_angle(self,angle):
        self.rudder_angle = angle
        self.rudder_servo.set_position(angle)

    def _turn_angle(self,track,requested_heading):
        diff = requested_heading - track
        if diff <= -180:
            diff = diff + 360
        if diff > 180:
            diff = diff - 360
        return diff