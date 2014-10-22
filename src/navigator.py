import math

class Navigator():
    def __init__(self,gps,helm,globe):
        self.gps = gps
        self.helm = helm
        self.globe = globe
        
    def to(self,waypoint, callback, *args):
        self.navigating_to = waypoint
        self.callback_on_arrived = callback
        self.callback_args = args

        self.check_progress()

    def check_progress(self):
        if self._arrived():
            self.callback_on_arrived(*self.callback_args)
        else:
            bearing = self.globe.bearing(self.gps.position, self.navigating_to.position)
            self.helm.steer(bearing,self.check_progress)

    def _error_radius(self,position):
        return math.sqrt(position.lat_error * position.lat_error + position.long_error * position.long_error)
        
    def _arrived(self):
        distance_left =  self.globe.distance_between(self.gps.position, self.navigating_to.position)
        tolerance = self._error_radius(self.gps.position) + float(self.navigating_to.tolerance)
        return distance_left <= tolerance
