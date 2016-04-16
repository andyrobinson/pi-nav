import sys
from events import Event

class Follower():
    def __init__(self,exchange,navigator,logger):
        self.navigator = navigator
        self.logger = logger
        self.exchange = exchange
        exchange.subscribe("arrived",self.next)

    def follow_route(self,waypoints):
        while waypoints:
            try:
                next_waypoint = waypoints[0]
                self.logger.info('Follower, next waypoint {:+f},{:+f}'.format(next_waypoint.latitude, next_waypoint.longitude))
                self.navigator.to(next_waypoint)
                waypoints = waypoints[1:]

            except(KeyboardInterrupt):
                quit()
            except:
                try:
                    etype,e,traceback = sys.exc_info()
                    print("oops: " + etype.__name__)
                    self.logger.error('Follower, {0}: {1}'.format(etype.__name__,', '.join(str(x) for x in e.args)))
                except:
                    pass

        self.logger.info('Follower, all waypoints reached, navigation complete')

    def follow(self,waypoints):
        self.waypoints = waypoints
        self._navigate_to_next_waypoint()

    def next(self,arrived_event):
        self.waypoints = self.waypoints[1:]
        if self.waypoints:
            self._navigate_to_next_waypoint()
        else:
            self.logger.info('Follower, all waypoints reached, navigation complete')

    def _navigate_to_next_waypoint(self):
        next_waypoint = self.waypoints[0]
        self.logger.info('Follower, next waypoint {:+f},{:+f}'.format(next_waypoint.latitude, next_waypoint.longitude))
        self.exchange.publish(Event("navigate",next_waypoint))
