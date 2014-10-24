import sys

class Follower():
    def __init__(self,navigator, logger):
        self.navigator = navigator
        self.logger = logger
        
    def follow_route(self,waypoints):
        while waypoints:
            try:        
                next_waypoint = waypoints[0]
                self.logger.info('Follower, next waypoint {:+f},{:+f}'.format(next_waypoint.longitude, next_waypoint.latitude))
                self.navigator.to(next_waypoint)
                waypoints = waypoints[1:]
            except:
                try:
                    etype,e,traceback = sys.exc_info()
                    self.logger.error('Follower, {0}: {1}'.format(etype.__name__,', '.join(str(x) for x in e.args)))
                except:
                    pass
            
        self.logger.info('Follower, all waypoints reached, navigation complete')