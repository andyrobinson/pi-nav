from math import copysign
from nan import isNaN
from bearing import angle_between

class Helm():
    def __init__(self,sensors,rudder_servo,timer,config):
        self.sensors = sensors
        self.rudder_servo = rudder_servo
        self._set_rudder_angle(0)
        self.config = config
        self.timer = timer
        self.previous_track = 0
        self.sleep_time = config['sleep time']

    def steer_course(self,requested_heading,for_seconds):
        remaining_seconds = for_seconds
        while remaining_seconds > 0:
            self.steer(requested_heading)
            self.timer.wait_for(self.sleep_time)
            remaining_seconds = remaining_seconds - self.sleep_time

    def steer(self,requested_heading):
        track = self.sensors.track

        if isNaN(track):
            self._set_rudder_angle(0)
        else:
            turn_angle = angle_between(track,requested_heading)
            rate_of_turn = angle_between(self.previous_track,track)
            ignore_below = self.config['ignore deviation below']

            if abs(turn_angle) <  ignore_below and abs(rate_of_turn) < ignore_below:
                return

            self._set_rudder_angle(self._calculate_rudder_angle(turn_angle,rate_of_turn))
            self.previous_track = track

    def _calculate_rudder_angle(self,turn_angle,rate_of_turn):
        rate_adjusted_turn_angle = self.rudder_angle + (turn_angle - rate_of_turn)
        unsigned_rudder_angle = min(self.config['full deflection'],abs(rate_adjusted_turn_angle))
        return copysign(unsigned_rudder_angle,rate_adjusted_turn_angle)

    def _set_rudder_angle(self,angle):
        self.rudder_angle = angle
        self.rudder_servo.set_position(angle)

