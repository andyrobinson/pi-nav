from bearing import angle_between, to_360
from math import sin,radians,copysign

class SailingHelm:

    def __init__(self,sensors,helm,config):
        self.config = config
        self.sensors = sensors
        self.helm = helm
        self.no_go = self.config['no go angle']

    def steer_course(self,requested_heading,for_seconds):
        wind_course_angle = angle_between(requested_heading, self.sensors.wind_direction)

        if abs(wind_course_angle) <= self.no_go:
            self._tack(requested_heading, wind_course_angle, for_seconds)
        else:
            self.helm.steer_course(requested_heading, for_seconds, self.no_go)

    def _tack(self, requested_heading, wind_course_angle, for_seconds):
        deflection = self._initial_tack_deflection(wind_course_angle)
        leg1, leg2 = self._leg_times(deflection, for_seconds)
        first_tack_course = requested_heading + deflection

        if leg2 <= self.config['min tack duration']:
            self.helm.steer_course(first_tack_course, for_seconds,self.no_go)
        else:
            self.helm.steer_course(to_360(first_tack_course), leg1,self.no_go)
            self.helm.steer_course(to_360(first_tack_course - copysign(2 * self.no_go, deflection)), leg2,self.no_go)

    def _leg_times(self,steering_deflection,time):
        theta1 = abs(steering_deflection)
        theta2 = 2 * self.no_go - theta1
        tack_angle = 180 - 2 * self.no_go
        t1 = float(time) * sin(radians(theta2)) / sin(radians(tack_angle))
        t2 = float(time) * sin(radians(theta1)) / sin(radians(tack_angle))
        return (round(t1),round(t2))

    def _initial_tack_deflection(self,wind_course_angle):
        return - copysign(self.no_go - abs(wind_course_angle),wind_course_angle)

