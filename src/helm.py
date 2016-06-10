from math import copysign
from nan import isNaN
from bearing import angle_between
from events import EventName, Event

class Helm():
    def __init__(self,exchange,sensors,rudder_servo,logger,config):
        self.sensors = sensors
        self.rudder_servo = rudder_servo
        self.rudder_angle = 0
        self.logger = logger
        self.previous_heading = 0
        self.requested_heading = 0
        self.on_course_count = 0
        self.exchange = exchange
        self.config = config
        self.ignore_below = config['ignore deviation below']
        self.full_deflection = config['full deflection']
        self.on_course_threshold = config['on course threshold']
        self.exchange.subscribe(EventName.set_course,self.set_course)
        self.exchange.subscribe(EventName.check_course,self.check_course)
        self.exchange.publish(Event(EventName.every,seconds=config['on course check interval'],next_event=Event(EventName.check_course)))

    def set_course(self,set_course_event):
        self.requested_heading = set_course_event.heading
        self._start_turning()
        self.turn(Event(EventName.tick))

    def turn(self,tick_event):
        heading = self.sensors.compass_heading_instant
        self._check_on_course(heading)
        self._steer(heading)

    def check_course(self,check_course_event):
        heading = self.sensors.compass_heading_average
        if abs(angle_between(heading,self.requested_heading)) > self.on_course_threshold:
            self._start_turning()
        self._steer(heading)

    def _start_turning(self):
        self.exchange.subscribe(EventName.tick,self.turn)
        self.on_course_count = 0

    def _stop_turning(self):
        self.exchange.unsubscribe(EventName.tick,self.turn)

    def _check_on_course(self,heading):
        if self._on_course(heading):
            self.on_course_count += 1
            if self.on_course_count >= self.config['turn on course min count']:
                self._stop_turning()
        else:
            self.on_course_count = 0

    def _rate_of_turn(self,heading):
        return angle_between(self.previous_heading,heading)

    def _deviation(self,heading):
        return angle_between(heading,self.requested_heading)

    def _on_course(self,heading):
        return abs(self._deviation(heading)) < self.ignore_below and abs(self._rate_of_turn(heading)) < self.ignore_below

    def _steer(self,heading):
        if isNaN(heading):
            self._set_rudder_angle(0)
            return

        if not self._on_course(heading):
            new_rudder_angle = self._calculate_rudder_angle(heading)
            self.logger.debug(
                'Helm, steering {:.1f}, heading {:.1f}, rate of turn {:+.1f}, rudder {:+.1f}, new rudder {:+.1f}'
                .format(self.requested_heading, heading, self._rate_of_turn(heading), self.rudder_angle, new_rudder_angle))
            self._set_rudder_angle(new_rudder_angle)
            self.previous_heading = heading

    def _calculate_rudder_angle(self,heading):
        rate_adjusted_turn_angle = self.rudder_angle - (self._deviation(heading) - self._rate_of_turn(heading))
        unsigned_rudder_angle = min(self.full_deflection,abs(rate_adjusted_turn_angle))
        return copysign(unsigned_rudder_angle,rate_adjusted_turn_angle)

    def _set_rudder_angle(self,angle):
        self.rudder_angle = angle
        self.rudder_servo.set_position(angle)
