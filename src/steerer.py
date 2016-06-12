from math import copysign
from nan import isNaN
from bearing import angle_between

class Steerer():
    def __init__(self,rudder_servo,logger,config):
        self.config = config
        self.rudder_angle = 0
        self.rudder_servo = rudder_servo
        self.logger = logger
        self.ignore_below = config['ignore deviation below']
        self.full_deflection = config['full deflection']

    def on_course(self,requested_heading,heading,rate_of_turn):
        return abs(self._deviation(requested_heading,heading)) < self.ignore_below and abs(rate_of_turn) < self.ignore_below

    def steer(self,requested_heading,heading,rate_of_turn):
        if isNaN(heading):
            self._set_rudder_angle(0)
            return

        if not self.on_course(requested_heading,heading,rate_of_turn):
            new_rudder_angle = self._calculate_rudder_angle(requested_heading,heading,rate_of_turn)
            self.logger.debug(
                'Helm, steering {:.1f}, heading {:.1f}, rate of turn {:+.1f}, rudder {:+.1f}, new rudder {:+.1f}'
                .format(requested_heading, heading, rate_of_turn, self.rudder_angle, new_rudder_angle))
            self._set_rudder_angle(new_rudder_angle)

    def _deviation(self,requested_heading,heading):
        return angle_between(heading,requested_heading)

    def _calculate_rudder_angle(self,requested_heading,heading,rate_of_turn):
        rate_adjusted_turn_angle = self.rudder_angle - (self._deviation(requested_heading,heading) - rate_of_turn)
        unsigned_rudder_angle = min(self.full_deflection,abs(rate_adjusted_turn_angle))
        return copysign(unsigned_rudder_angle,rate_adjusted_turn_angle)

    def _set_rudder_angle(self,angle):
        self.rudder_angle = angle
        self.rudder_servo.set_position(angle)
