from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, PropertyMock, call
from helm import Helm
from config import CONFIG
from nan import NaN
from events import Exchange, Event,EventName
from test_utils import EventTestCase
from copy import deepcopy
from steerer import Steerer

TEST_CONFIG = deepcopy(CONFIG['helm'])
TEST_CONFIG['turn on course min count'] = 3

class TestHelm(EventTestCase):

    def setUp(self):
        super(TestHelm, self).setUp()
        self.sensors = Mock()
        self.logger = Mock()
        self.steerer = Mock()
        self.helm = Helm(self.exchange, self.sensors,self.steerer,self.logger, TEST_CONFIG)
        self.helm.previous_heading = 180

    def currently_tracking(self,previous_heading, current_track, rudder_angle=0):
        self.sensors.compass_heading_instant = current_track
        self.sensors.compass_heading_average = NaN
        self.sensors.rate_of_turn = current_track - previous_heading
        self.sensors.rate_of_turn_average = self.sensors.rate_of_turn

    def averagely_tracking(self,previous_heading, current_track):
        self.sensors.compass_heading_average = current_track
        self.sensors.compass_heading_instant = NaN
        self.sensors.rate_of_turn = 0
        self.sensors.rate_of_turn_average = current_track - previous_heading

    def test_should_steer_following_set_course_event(self):
        self.currently_tracking(204,200)
        self.exchange.publish(Event(EventName.set_course,heading=196))
        self.steerer.steer.assert_called_with(196,200,-4)

        self.sensors.track = 202
        self.sensors.rate_of_turn = -20
        self.exchange.publish(Event(EventName.tick))
        self.steerer.steer.assert_called_with(196,200,-20)

    def test_should_use_instant_heading_when_turning(self):
        self.helm.requested_heading = 5
        self.currently_tracking(340,350)
        self.helm.turn(Event(EventName.tick))

        self.steerer.steer.assert_called_with(5,350,10)

    def test_should_use_average_heading_when_checking_course(self):
        self.helm.requested_heading = 5
        self.averagely_tracking(335,350)
        self.helm.check_course(Event(EventName.tick))

        self.steerer.steer.assert_called_with(5,350,15)

    def test_should_trigger_turning_if_off_course_by_more_than_configured_20_degrees(self):
        self.exchange.unsubscribe(EventName.tick,self.helm.turn)
        self.helm.requested_heading = 90
        self.averagely_tracking(50,60)
        self.helm.check_course(Event(EventName.tick))

        self.steerer.steer.assert_called_with(90,60,10)
        self.assertIn(self.helm.turn,self.exchange.register[EventName.tick])

    def test_should_immediately_change_to_turning_when_course_is_set(self):
        self.exchange.unsubscribe(EventName.tick,self.helm.turn)
        self.currently_tracking(50,60)

        self.exchange.publish(Event(EventName.set_course,heading=90))

        self.steerer.steer.assert_called_with(90,60,10)
        self.assertIn(self.helm.turn,self.exchange.register[EventName.tick])

    def test_should_unsubscribe_turn_to_tick_event_when_on_course_after_configured_three_checks(self):
        self.currently_tracking(120,125)
        self.exchange.publish(Event(EventName.set_course,heading=90))

        self.currently_tracking(95,85)
        self.exchange.publish(Event(EventName.tick))
        self.currently_tracking(85,87)
        self.exchange.publish(Event(EventName.tick))
        self.currently_tracking(85,87)
        self.exchange.publish(Event(EventName.tick))
        self.currently_tracking(85,87)
        self.exchange.publish(Event(EventName.tick))

        self.assertNotIn(self.helm.turn,self.exchange.register[EventName.tick])

    def test_should_continue_turning_if_on_course_with_high_rate_of_turn(self):
        self.currently_tracking(95,85)
        self.exchange.publish(Event(EventName.set_course,heading=90))
        self.steerer.on_course.side_effect = [False,False,False,False]

        self.currently_tracking(85,95)
        self.exchange.publish(Event(EventName.tick))
        self.currently_tracking(95,85)
        self.exchange.publish(Event(EventName.tick))
        self.currently_tracking(85,95)
        self.exchange.publish(Event(EventName.tick))
        self.currently_tracking(95,85)
        self.exchange.publish(Event(EventName.tick))

        self.assertIn(self.helm.turn,self.exchange.register[EventName.tick])

    def test_should_subscribe_check_course_every_10_seconds(self):
        self.listen(EventName.every)
        helm = Helm(self.exchange, self.sensors,self.steerer,self.logger, TEST_CONFIG)

        self.assertEqual(len(self.events[EventName.every]),1)
