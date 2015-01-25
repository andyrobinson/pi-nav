import math
from nan import isNaN

MIN_SPEED_FOR_STEER_TIME_CALCULATION = 0.01
DISTANCE_FRACTION_TO_STEER = 0.75

class Navigator():
    def __init__(self,sensors,course_steerer,globe,logger,config):
        self.course_steerer = course_steerer
        self.sensors = sensors
        self.globe = globe
        self.logger = logger
        self.bearing = 0.0
        self.config = config
        
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

            self.course_steerer.steer_course(self.bearing, time_to_steer)
            current_position = self.sensors.position

        self.logger.info('Navigator, arrived at {:+f},{:+f}'.format(destination_waypoint.latitude,destination_waypoint.longitude))

    def _time_to_waypoint(self, position, destination_waypoint):
        min_time = self.config['min time to steer']
        max_time = self.config['max time to steer']
        speed = max(MIN_SPEED_FOR_STEER_TIME_CALCULATION,self.sensors.speed)
        #by some quirk max and min remove NaN if tNhere is a real number in the first position
        result = min(max_time, max(min_time, DISTANCE_FRACTION_TO_STEER * self._distance(position,destination_waypoint)/speed))
        return int(result)

    def _error_radius(self,position):
        return math.sqrt(position.lat_error * position.lat_error + position.long_error * position.long_error)
        
    def _arrived(self,position,destination_waypoint):
        tolerance = self._error_radius(position) + float(destination_waypoint.tolerance)
        return self._distance(position,destination_waypoint) <= tolerance

    def _distance(self,position,destination_waypoint):
        return self.globe.distance_between(position, destination_waypoint.position)