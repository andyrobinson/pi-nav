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
        self.previous_track = 0
        self.requested_heading = 0
        self.exchange = exchange
        self.ignore_below = config['ignore deviation below']
        self.full_deflection = config['full deflection']
        self.exchange.subscribe(EventName.set_course,self.set_course)
        self.exchange.subscribe(EventName.tick,self.steer)

    def set_course(self,set_course_event):
        self.requested_heading = set_course_event.heading
        self.steer(Event(EventName.tick))

    def steer(self,tick_event):
        track = self.sensors.track

        if isNaN(track):
            self._set_rudder_angle(0)
            return

        deviation = angle_between(track,self.requested_heading)
        rate_of_turn = angle_between(self.previous_track,track)

        if abs(deviation) > self.ignore_below or abs(rate_of_turn) > self.ignore_below:
            self._correct_steering(rate_of_turn, self.requested_heading, track, deviation)

    def _calculate_rudder_angle(self,deviation,rate_of_turn):
        rate_adjusted_turn_angle = self.rudder_angle - (deviation - rate_of_turn)
        unsigned_rudder_angle = min(self.full_deflection,abs(rate_adjusted_turn_angle))
        return copysign(unsigned_rudder_angle,rate_adjusted_turn_angle)

    def _set_rudder_angle(self,angle):
        self.rudder_angle = angle
        self.rudder_servo.set_position(angle)

    def _correct_steering(self, rate_of_turn, requested_heading, track, deviation):
        new_rudder_angle = self._calculate_rudder_angle(deviation, rate_of_turn)
        self.logger.debug(
            'Helm, steering {:.1f}, tracking {:.1f}, rate of turn {:+.1f}, rudder {:+.1f}, new rudder {:+.1f}'
            .format(requested_heading, track, rate_of_turn, self.rudder_angle, new_rudder_angle))
        self._set_rudder_angle(new_rudder_angle)
        self.previous_track = track
