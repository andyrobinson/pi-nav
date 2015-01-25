from math import copysign
from nan import isNaN
from bearing import angle_between

class Helm():
    def __init__(self,sensors,rudder_servo,timer,logger, config):
        self.sensors = sensors
        self.rudder_servo = rudder_servo
        self.rudder_angle = 0
        self.config = config
        self.timer = timer
        self.logger = logger
        self.previous_track = 0
        self.sleep_time = config['sleep time']

    def steer(self,requested_heading):
        track = self.sensors.track

        if isNaN(track):
            self._set_rudder_angle(0)
            return

        turn_angle = angle_between(track,requested_heading)
        rate_of_turn = angle_between(self.previous_track,track)
        ignore_below = self.config['ignore deviation below']

        if abs(turn_angle) > ignore_below or abs(rate_of_turn) > ignore_below:
            self._correct_steering(rate_of_turn, requested_heading, track, turn_angle)

    def _calculate_rudder_angle(self,turn_angle,rate_of_turn):
        rate_adjusted_turn_angle = self.rudder_angle - (turn_angle - rate_of_turn)
        unsigned_rudder_angle = min(self.config['full deflection'],abs(rate_adjusted_turn_angle))
        return copysign(unsigned_rudder_angle,rate_adjusted_turn_angle)

    def _set_rudder_angle(self,angle):
        self.rudder_angle = angle
        self.rudder_servo.set_position(angle)

    def _correct_steering(self, rate_of_turn, requested_heading, track, turn_angle):
        new_rudder_angle = self._calculate_rudder_angle(turn_angle, rate_of_turn)
        self.logger.debug(
            'Helm, steering {:.1f}, tracking {:.1f}, rate of turn {:+.1f}, rudder {:+.1f}, new rudder {:+.1f}'
            .format(requested_heading, track, rate_of_turn, self.rudder_angle, new_rudder_angle))
        self._set_rudder_angle(new_rudder_angle)
        self.previous_track = track
