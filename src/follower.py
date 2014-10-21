class Follower():
    def __init__(self,navigator, logger):
        self.navigator = navigator
        self.logger = logger
        
    def follow_route(self,waypoints):
        if waypoints:
            next_waypoint = waypoints[0]
            self.logger.info('Navigating to {:+f},{:+f}'.format(next_waypoint.longitude, next_waypoint.latitude))
            self.navigator.to(waypoints[0], self.follow_route , waypoints[1:])
        else:
            self.logger.info('Navigation complete')