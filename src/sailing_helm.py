from bearing import angle_between, to_360
from math import sin,radians,copysign
from events import EventName, Event

class SailingHelm:

    def __init__(self, exchange, sensors, logger, config):
        self.exchange = exchange
        self.sensors = sensors
        self.logger = logger
        self.config = config
        self.no_go = self.config['no go angle']
        self.exchange.subscribe(EventName.sail_course, self.sail_course)
        self.exchange.subscribe(EventName.tack, self.tack)

    def sail_course(self, sail_to_event):
        requested_heading = sail_to_event.heading
        self.logger.debug('SailingHelm: sail course {:5.1f}'.format(requested_heading))
        self._tack_if_needed(requested_heading, sail_to_event.seconds)

    # Strickly speaking not necessary, but will help with debugging
    def tack(self, tack_event):
        tack_heading = tack_event.heading
        self.logger.debug('SailingHelm: tack on {:5.1f}'.format(tack_heading))
        self.exchange.publish(Event(EventName.set_course, heading=tack_heading))

    def _tack_if_needed(self,requested_heading, time_to_next_review):
        wind_course_angle = angle_between(requested_heading, self.sensors.wind_direction_abs_average)

        if abs(wind_course_angle) <= self.no_go:
            self._start_tack(requested_heading, wind_course_angle, time_to_next_review)
        else:
            self.exchange.publish(Event(EventName.set_course, heading=requested_heading))

    def _start_tack(self, requested_heading, wind_course_angle, time_to_next_review):
        deflection = self._initial_tack_deflection(wind_course_angle)
        leg1, leg2 = self._leg_times(deflection, time_to_next_review)
        first_tack_course = to_360(requested_heading + deflection)
        second_tack_course = to_360(first_tack_course - copysign(2 * self.no_go, deflection))
        self.logger.debug('SailingHelm: starting tack on {:5.1f} for {:5.0f} seconds'.format(first_tack_course, leg1))
        print("tacks " + str(first_tack_course) + " for " + str(leg1) + "s and then " + str(second_tack_course)) + " for " + str(leg2)

        if leg2 <= self.config['min tack duration']:
            self.exchange.publish(Event(EventName.tack, heading=first_tack_course))
        else:
            second_tack_event = Event(EventName.tack, heading = second_tack_course)
            self.exchange.publish(Event(EventName.tack, heading=first_tack_course))
            self.exchange.publish(Event(EventName.after, seconds = leg1, next_event= second_tack_event))

    def _leg_times(self,steering_deflection,time):
        theta1 = abs(steering_deflection)
        theta2 = 2 * self.no_go - theta1
        tack_angle = 180 - 2 * self.no_go
        t1 = float(time) * sin(radians(theta2)) / sin(radians(tack_angle))
        t2 = float(time) * sin(radians(theta1)) / sin(radians(tack_angle))
        ratio_to_keep_total_time = time / (t1 + t2)
        return (round(t1 * ratio_to_keep_total_time), round(t2 * ratio_to_keep_total_time))

    def _initial_tack_deflection(self,wind_course_angle):
        return - copysign(self.no_go - abs(wind_course_angle),wind_course_angle)

