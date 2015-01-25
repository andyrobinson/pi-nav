from bearing import angle_between
from math import copysign

class CourseSteerer:
    def __init__(self,sensors, helm, timer,config):
        self.timer = timer
        self.helm = helm
        self.sensors = sensors
        self.sleep_time = config['sleep time']

    def steer_course(self, heading, duration, no_go_angle = 0):
        remaining_seconds = duration
        while remaining_seconds > 0:
            self._steer_avoiding_no_go_area(heading, no_go_angle)
            self.timer.wait_for(self.sleep_time)
            remaining_seconds = remaining_seconds - self.sleep_time

    def _steer_avoiding_no_go_area(self, heading, no_go_angle):
        heading_wind_diff = angle_between(heading, self.sensors.wind_direction)
        if abs(heading_wind_diff) <= no_go_angle:
            self.helm.steer(heading - copysign(no_go_angle - abs(heading_wind_diff), heading_wind_diff))
        else:
            self.helm.steer(heading)
