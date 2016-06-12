from math import copysign
from nan import isNaN
from bearing import angle_between
from events import EventName, Event

class Steerer():
    def __init__(self,rudder_servo,logger,config):
        self.config = config
        self.rudder_angle = 0
        self.rudder_servo = rudder_servo
        self.logger = logger
        self.ignore_below = config['ignore deviation below']
        self.full_deflection = config['full deflection']

    def on_course(self,requested_heading,heading,rate_of_turn):
        return abs(self._deviation(requested_heading,heading)) < self.ignore_below and abs(rate_of_turn) < self.ignore_below

    def steer(self,requested_heading,heading,rate_of_turn):
        if isNaN(heading):
            self._set_rudder_angle(0)
            return

        if not self.on_course(requested_heading,heading,rate_of_turn):
            new_rudder_angle = self._calculate_rudder_angle(requested_heading,heading,rate_of_turn)
            self.logger.debug(
                'Helm, steering {:.1f}, heading {:.1f}, rate of turn {:+.1f}, rudder {:+.1f}, new rudder {:+.1f}'
                .format(requested_heading, heading, rate_of_turn, self.rudder_angle, new_rudder_angle))
            self._set_rudder_angle(new_rudder_angle)

    def _deviation(self,requested_heading,heading):
        return angle_between(heading,requested_heading)

    def _calculate_rudder_angle(self,requested_heading,heading,rate_of_turn):
        rate_adjusted_turn_angle = self.rudder_angle - (self._deviation(requested_heading,heading) - rate_of_turn)
        unsigned_rudder_angle = min(self.full_deflection,abs(rate_adjusted_turn_angle))
        return copysign(unsigned_rudder_angle,rate_adjusted_turn_angle)

    def _set_rudder_angle(self,angle):
        self.rudder_angle = angle
        self.rudder_servo.set_position(angle)

class Helm():
    def __init__(self,exchange,sensors,rudder_servo,logger,config):
        self.sensors = sensors
        self.logger = logger
        self.requested_heading = 0
        self.on_course_count = 0
        self.exchange = exchange
        self.on_course_count_threshold = config['turn on course min count']
        self.on_course_threshold = config['on course threshold']
        self.steerer = Steerer(rudder_servo,logger,config)
        self.exchange.subscribe(EventName.set_course,self.set_course)
        self.exchange.subscribe(EventName.check_course,self.check_course)
        self.exchange.publish(Event(EventName.every,seconds=config['on course check interval'],next_event=Event(EventName.check_course)))

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
        heading = self.sensors.compass_heading_average
        rate_of_turn = self.sensors.rate_of_turn_average
        if abs(angle_between(heading,self.requested_heading)) > self.on_course_threshold:
            self._start_turning()
        self.steerer.steer(self.requested_heading,heading,rate_of_turn)

    def _start_turning(self):
        self.exchange.subscribe(EventName.tick,self.turn)
        self.on_course_count = 0

    def _stop_turning(self):
        self.exchange.unsubscribe(EventName.tick,self.turn)

    def _check_on_course(self,heading,rate_of_turn):
        if self.steerer.on_course(self.requested_heading,heading,rate_of_turn):
            self.on_course_count += 1
            if self.on_course_count >= self.on_course_count_threshold:
                self._stop_turning()
        else:
            self.on_course_count = 0
