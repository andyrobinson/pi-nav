FULL_LEFT = 30

class Helm():
    def __init__(self,sensors,rudder_servo):
        self.sensors = sensors
        self.rudder_servo = rudder_servo

    def steer(self,requested_heading):
        angular_diff = self._angular_diff(self.sensors.track,requested_heading)
        if abs(angular_diff) < 5:
            return
        if angular_diff < 0:
            self.rudder_servo.set_position(FULL_LEFT)

    def _angular_diff(self,track,requested_heading):
        diff = requested_heading - track
        if diff <= -180:
            diff = diff + 360
        if diff > 180:
            diff = diff - 360
        return diff