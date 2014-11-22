import math
from nan import isNaN

class Navigator():
    def __init__(self,sensors,helm,globe,logger):
        self.sensors = sensors
        self.helm = helm
        self.globe = globe
        self.logger = logger
        self.bearing = 0.0
        
    def to(self,destination_waypoint):
        current_position = self.sensors.position

        while not self._arrived(current_position,destination_waypoint):
            time_to_steer = self._time_to_waypoint(current_position,destination_waypoint)
            bearing = self.globe.bearing(current_position, destination_waypoint.position)

            if isNaN(bearing):
                self.logger.warn('Navigator, no information from sensors, continuing on bearing {:5.1f}'.format(self.bearing))
            else:
                self.bearing = bearing
                self.logger.info('Navigator, steering to {:+f},{:+f}, bearing {:5.1f}, distance {:.1f}m'
                    .format(destination_waypoint.latitude,destination_waypoint.longitude, bearing, self._distance(current_position,destination_waypoint)))

            self.helm.steer_course(self.bearing, time_to_steer)
            current_position = self.sensors.position

        self.logger.info('Navigator, arrived at {:+f},{:+f}'.format(destination_waypoint.latitude,destination_waypoint.longitude))

    def _time_to_waypoint(self, position, destination_waypoint):
        result = self._distance(position,destination_waypoint)/self.sensors.speed
        if isNaN(result) or result < 5:
            result = 5
        return int(result)

    def _error_radius(self,position):
        return math.sqrt(position.lat_error * position.lat_error + position.long_error * position.long_error)
        
    def _arrived(self,position,destination_waypoint):
        tolerance = self._error_radius(position) + float(destination_waypoint.tolerance)
        return self._distance(position,destination_waypoint) <= tolerance

    def _distance(self,position,destination_waypoint):
        return self.globe.distance_between(position, destination_waypoint.position)