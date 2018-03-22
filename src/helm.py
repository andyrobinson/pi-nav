from math import copysign
from nan import isNaN
from bearing import angle_between
from events import EventName, Event

class Helm():
    def __init__(self,exchange,sensors,steerer,logger,config):
        self.sensors = sensors
        self.logger = logger
        self.requested_heading = 0
        self.exchange = exchange
        self.steerer = steerer

        self.exchange.subscribe(EventName.set_course,self.set_course)
        self.exchange.subscribe(EventName.check_course,self.check_course)
        self.exchange.publish(Event(EventName.every,seconds=config['on course check interval'],next_event=Event(EventName.check_course)))

    def set_course(self,set_course_event):
        self.requested_heading = set_course_event.heading
        self.check_course(set_course_event)

    def check_course(self,unused_check_course_event):
        heading = self.sensors.compass_heading_average
        rate_of_turn = self.sensors.rate_of_turn_average
        if not(self.steerer.on_course(self.requested_heading,heading,rate_of_turn)):
            self.steerer.steer(self.requested_heading,heading,rate_of_turn)
