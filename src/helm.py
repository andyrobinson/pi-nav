from math import copysign

class Helm():
    def __init__(self,sensors,rudder_servo,config):
        self.sensors = sensors
        self.rudder_servo = rudder_servo
        self._set_rudder_angle(0)
        self.full_deflection = config['full deflection']

    def steer(self,requested_heading):
        int_track = int(round(self.sensors.track))
        int_heading = int(round(requested_heading))
        turn_angle = self._turn_angle(int_track,int_heading)

        if abs(turn_angle) < 5 and abs(self.rudder_angle) < 5:
            return

        self._set_rudder_angle(self._calculate_rudder_angle(turn_angle))

    def _calculate_rudder_angle(self,turn_angle):
        unsigned_rudder_angle = min(self.full_deflection,int(abs(turn_angle)/2))
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