from bearing import to_360,angle_between

class FakeSensors:
    def __init__(self,gps,wind_direction,compass_heading):
        self.gps = gps
        self.time = 0
        self.speed = 1
        self.track_error = 1
        self.speed_error = 0.1
        self.rate_of_turn = 1
        self.rate_of_turn_average = 1
        self.wind_direction_abs_average = wind_direction
        self.wind_direction_relative_instant = to_360(angle_between(wind_direction,compass_heading))
        self.wind_direction_relative_average = self.wind_direction_relative_instant
        self.compass_heading_average = compass_heading
        self.compass_heading_smoothed = compass_heading

    @property
    def hasfix(self):
        return self.gps.hasfix

    @property
    def position(self):
        return self.gps.position

    @property
    def track(self):
        return self.gps.track

    def update_averages(self,tick_event):
        pass
