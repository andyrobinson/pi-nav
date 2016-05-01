import sys
from events import Event,EventName

class Follower():
    def __init__(self,exchange,navigator,waypoints,logger):
        self.navigator = navigator
        self.logger = logger
        self.exchange = exchange
        self.waypoints = waypoints
        exchange.subscribe(EventName.arrived,self.next)
        exchange.subscribe(EventName.start,self.next)

    def next(self,unused_event):
        if self.waypoints:
            self._navigate_to_next_waypoint()
        else:
            self.logger.info('Follower, all waypoints reached, navigation complete')
            self.exchange.publish(Event(EventName.end))

    def _navigate_to_next_waypoint(self):
        next_waypoint = self.waypoints[0]
        self.waypoints = self.waypoints[1:]
        self.logger.info('Follower, next waypoint {:+f},{:+f}'.format(next_waypoint.latitude, next_waypoint.longitude))
        self.exchange.publish(Event(EventName.navigate,next_waypoint))
