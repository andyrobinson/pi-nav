import math

class Navigator():
    def __init__(self,gps,helm,globe,logger):
        self.gps = gps
        self.helm = helm
        self.globe = globe
        self.logger = logger
        
    def to(self,waypoint, callback, *args):
        self.navigating_to = waypoint
        self.callback_on_arrived = callback
        self.callback_args = args

        self.check_progress()

    def check_progress(self):
        if self._arrived():
            self.logger.info('Navigator, arrived at {:+f},{:+f}'.format(self.navigating_to.latitude,self.navigating_to.longitude))
            self.callback_on_arrived(*self.callback_args)
        else:
            bearing = self.globe.bearing(self.gps.position, self.navigating_to.position)
            self.logger.info('blah')
            self.logger.info('Navigator, steering to {:+f},{:+f}, bearing {:5.1f}, distance {:.1f}m'
                .format(self.navigating_to.latitude,self.navigating_to.longitude, bearing, self._distance()))
            self.helm.steer(bearing,self.check_progress)

    def _error_radius(self,position):
        return math.sqrt(position.lat_error * position.lat_error + position.long_error * position.long_error)
        
    def _arrived(self):
        tolerance = self._error_radius(self.gps.position) + float(self.navigating_to.tolerance)
        return self._distance() <= tolerance

    def _distance(self):
        return self.globe.distance_between(self.gps.position, self.navigating_to.position)