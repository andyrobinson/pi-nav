from math import copysign
from nan import isNaN
from bearing import angle_between

class Steerer():
    def __init__(self,rudder_servo,logger,config):
        self.config = config
        self.rudder_angle = 0
        self.rudder_servo = rudder_servo
        self.logger = logger
        self.full_rudder_deflection = config['full rudder deflection']
        self.ignore_course_deviation_below = config['ignore deviation below']
        self.ignore_rate_of_turn_below = config['ignore rate of turn below']
        self.rate_of_turn_factor = config['rate of turn factor']
        self.deviation_factor = config['deviation factor']

    def on_course(self,requested_heading,heading,rate_of_turn):
        return (abs(self._deviation(requested_heading,heading)) < self.ignore_course_deviation_below
                and abs(rate_of_turn) < self.ignore_rate_of_turn_below)

    def steer(self,requested_heading,heading,rate_of_turn,rudder_deflection_factor = 1):
        if isNaN(heading):
            self.logger.debug('Steerer, no valid heading, centralising rudder')
            self._set_rudder_angle(0)
            return

        if not self.on_course(requested_heading,heading,rate_of_turn):
            new_rudder_angle = self._calculate_rudder_angle(requested_heading,heading,rate_of_turn,rudder_deflection_factor)
            self.logger.debug(
                'Steerer, steering {:.1f}, heading {:.1f}, rate of turn {:+.1f}, rudder {:+.1f}, new rudder {:+.1f}'
                .format(requested_heading, heading, rate_of_turn, self.rudder_angle, new_rudder_angle))
            self._set_rudder_angle(new_rudder_angle)

    def _deviation(self,requested_heading,heading):
        return angle_between(heading,requested_heading)

    def _calculate_rudder_angle(self,requested_heading,heading,rate_of_turn,rudder_deflection_factor):
        rate_adjusted_turn_angle = self.rudder_angle - (
            self._deviation(requested_heading,heading) * self.deviation_factor
            - rate_of_turn * self.rate_of_turn_factor)
        unsigned_rudder_angle = min(self.full_rudder_deflection,abs(rate_adjusted_turn_angle))
        return copysign(unsigned_rudder_angle,rate_adjusted_turn_angle) * rudder_deflection_factor

    def _set_rudder_angle(self,angle):
        self.rudder_angle = angle
        self.rudder_servo.set_position(angle)
