import sys
from events import Event

class Follower():
    def __init__(self,exchange,navigator,waypoints,logger):
        self.navigator = navigator
        self.logger = logger
        self.exchange = exchange
        self.waypoints = waypoints
        exchange.subscribe(Event.arrived,self.next)
        exchange.subscribe(Event.start,self.next)

    def follow_route(self):
        while self.waypoints:
            try:
                next_waypoint = self.waypoints[0]
                self.logger.info('Follower, next waypoint {:+f},{:+f}'.format(next_waypoint.latitude, next_waypoint.longitude))
                self.navigator.to(next_waypoint)
                self.waypoints = self.waypoints[1:]

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

    def next(self,unused_event):
        if self.waypoints:
            self._navigate_to_next_waypoint()
        else:
            self.logger.info('Follower, all waypoints reached, navigation complete')
            self.exchange.publish(Event(Event.end))

    def _navigate_to_next_waypoint(self):
        next_waypoint = self.waypoints[0]
        self.waypoints = self.waypoints[1:]
        self.logger.info('Follower, next waypoint {:+f},{:+f}'.format(next_waypoint.latitude, next_waypoint.longitude))
        self.exchange.publish(Event(Event.navigate,next_waypoint))
