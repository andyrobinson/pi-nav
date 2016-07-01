from math import copysign
from nan import isNaN
from bearing import angle_between
from events import EventName, Event

class Helm():
    def __init__(self,exchange,sensors,steerer,logger,config):
        self.sensors = sensors
        self.logger = logger
        self.requested_heading = 0
        self.on_course_count = 0
        self.exchange = exchange
        self.steerer = steerer
        self.turning = False
        helm_config = config['helm']
        self.on_course_count_threshold = helm_config['turn on course min count']
        self.on_course_threshold = helm_config['on course threshold']
        self.reduction_factor = config['event source']['tick interval']/helm_config['on course check interval']

        self.exchange.subscribe(EventName.set_course,self.set_course)
        self.exchange.subscribe(EventName.check_course,self.check_course)
        self.exchange.publish(Event(EventName.every,seconds=helm_config['on course check interval'],next_event=Event(EventName.check_course)))

    def set_course(self,set_course_event):
        self.requested_heading = set_course_event.heading
        self._start_turning()
        self.turn(Event(EventName.tick))

    def turn(self,tick_event):
        heading = self.sensors.compass_heading_instant
        rate_of_turn = self.sensors.rate_of_turn
        self._check_on_course(heading,rate_of_turn)
        self.steerer.steer(self.requested_heading,heading,rate_of_turn)

    def check_course(self,check_course_event):
        if self.turning:
            return
        heading = self.sensors.compass_heading_average
        rate_of_turn = self.sensors.rate_of_turn_average
        if abs(angle_between(heading,self.requested_heading)) > self.on_course_threshold:
            self._start_turning()
        self.steerer.steer(self.requested_heading,heading,rate_of_turn,self.reduction_factor)

    def _start_turning(self):
        self.turning = True
        self.exchange.subscribe(EventName.tick,self.turn)
        self.on_course_count = 0

    def _stop_turning(self):
        self.turning = False
        self.exchange.unsubscribe(EventName.tick,self.turn)

    def _check_on_course(self,heading,rate_of_turn):
        if self.steerer.on_course(self.requested_heading,heading,rate_of_turn):
            self.on_course_count += 1
            if self.on_course_count >= self.on_course_count_threshold:
                self._stop_turning()
        else:
            self.on_course_count = 0
