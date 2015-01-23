from bearing import angle_between
from math import tan,radians,copysign

NO_GO_ANGLE = 45
MIN_TACK_DURATION = 5

class SailingHelm:

    def __init__(self,sensors,helm):
        self.sensors = sensors
        self.helm = helm

    def steer_course(self,requested_heading,for_seconds):
        wind_course_angle = angle_between(requested_heading, self.sensors.wind_direction)

        if abs(wind_course_angle) <= NO_GO_ANGLE:
            deflection = self._initial_tack_deflection(wind_course_angle)
            leg1, leg2 = self._leg_times(deflection,for_seconds)
            first_tack_course = requested_heading + deflection

            if leg2 <= MIN_TACK_DURATION:
                self.helm.steer_course(first_tack_course,for_seconds)
            else:
                self.helm.steer_course(first_tack_course,leg1)
                self.helm.steer_course(first_tack_course - copysign(2 * NO_GO_ANGLE,deflection),leg2)
        else:
            self.helm.steer_course(requested_heading,for_seconds)

    def _leg_times(self,steering_deflection,time):
        tan1 = tan(radians(abs(steering_deflection)))
        t1 = float(time) / (1 + tan1)
        t2 = time - t1
        return (round(t1),round(t2))

    def _initial_tack_deflection(self,wind_course_angle):
        return - copysign(NO_GO_ANGLE - abs(wind_course_angle),wind_course_angle)

