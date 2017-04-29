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

TEST_CONFIG = deepcopy(CONFIG)
HELM_CONFIG = TEST_CONFIG['helm']
HELM_CONFIG['turn on course min count'] = 3
HELM_CONFIG['turn steer interval'] = 3

class TestHelm(EventTestCase):

    def setUp(self):
        super(TestHelm, self).setUp()
        self.sensors = Mock()
        self.logger = Mock()
        self.steerer = Mock()
        self.helm = Helm(self.exchange, self.sensors,self.steerer,self.logger, HELM_CONFIG)
        self.helm.previous_heading = 180

    def reduction_factor(self):
        factor = float(HELM_CONFIG['turn steer interval'])/(HELM_CONFIG['on course check interval'])
        return factor

    def currently_tracking(self,previous_heading, current_track, rudder_angle=0):
        self.sensors.compass_heading_smoothed = current_track
        self.sensors.compass_heading_average = NaN
        self.sensors.rate_of_turn = current_track - previous_heading
        self.sensors.rate_of_turn_average = self.sensors.rate_of_turn

    def averagely_tracking(self,previous_heading, current_track):
        self.sensors.compass_heading_average = current_track
        self.sensors.compass_heading_smoothed = NaN
        self.sensors.rate_of_turn = 0
        self.sensors.rate_of_turn_average = current_track - previous_heading

    def test_should_steer_following_set_course_event(self):
        self.currently_tracking(204,200)
        self.exchange.publish(Event(EventName.set_course,heading=196))
        self.steerer.steer.assert_called_with(196,200,-4)

        self.sensors.track = 202
        self.sensors.rate_of_turn = -20
        self.exchange.publish(Event(EventName.steer))
        self.steerer.steer.assert_called_with(196,200,-20)

    def test_should_use_instant_heading_when_turning(self):
        self.helm.requested_heading = 5
        self.currently_tracking(340,350)
        self.helm.turn(Event(EventName.steer))

        self.steerer.steer.assert_called_with(5,350,10)

    def test_should_use_average_heading_and_reduction_factor_when_checking_course(self):
        self.helm.requested_heading = 5
        self.averagely_tracking(335,350)
        self.helm.check_course(Event(EventName.steer))

        self.steerer.steer.assert_called_with(5,350,15,self.reduction_factor())

    def test_should_trigger_turning_if_off_course_by_more_than_configured_20_degrees(self):
        self.exchange.unsubscribe(EventName.steer,self.helm.turn)
        self.helm.requested_heading = 90
        self.averagely_tracking(50,60)
        self.helm.check_course(Event(EventName.steer))

        self.steerer.steer.assert_called_with(90,60,10,self.reduction_factor())
        self.assertIn(self.helm.turn,self.exchange.register[EventName.steer])
        self.assertTrue(self.helm.turning)

    def test_should_immediately_change_to_turning_when_course_is_set(self):
        self.exchange.unsubscribe(EventName.steer,self.helm.turn)
        self.currently_tracking(50,60)

        self.exchange.publish(Event(EventName.set_course,heading=90))

        self.steerer.steer.assert_called_with(90,60,10)
        self.assertIn(self.helm.turn,self.exchange.register[EventName.steer])
        self.assertTrue(self.helm.turning)

    def test_should_unsubscribe_turn_to_steer_event_when_on_course_after_configured_three_checks(self):
        self.currently_tracking(120,125)
        self.exchange.publish(Event(EventName.set_course,heading=90))

        self.currently_tracking(95,85)
        self.exchange.publish(Event(EventName.steer))
        self.currently_tracking(85,87)
        self.exchange.publish(Event(EventName.steer))
        self.currently_tracking(85,87)
        self.exchange.publish(Event(EventName.steer))
        self.currently_tracking(85,87)
        self.exchange.publish(Event(EventName.steer))

        self.assertNotIn(self.helm.turn,self.exchange.register[EventName.steer])
        self.assertFalse(self.helm.turning)

    def test_should_continue_turning_if_on_course_with_high_rate_of_turn(self):
        self.currently_tracking(95,85)
        self.exchange.publish(Event(EventName.set_course,heading=90))
        self.steerer.on_course.side_effect = [False,False,False,False]

        self.currently_tracking(85,95)
        self.exchange.publish(Event(EventName.steer))
        self.currently_tracking(95,85)
        self.exchange.publish(Event(EventName.steer))
        self.currently_tracking(85,95)
        self.exchange.publish(Event(EventName.steer))
        self.currently_tracking(95,85)
        self.exchange.publish(Event(EventName.steer))

        self.assertIn(self.helm.turn,self.exchange.register[EventName.steer])
        self.assertTrue(self.helm.turning)

    def test_should_subscribe_check_course_every_10_seconds(self):
        self.listen(EventName.every)
        helm = Helm(self.exchange, self.sensors,self.steerer,self.logger, HELM_CONFIG)

        self.assertEqual(self.events[EventName.every][0].next_event.name,EventName.check_course)

    def test_should_generate_repeating_steer_event_according_to_config(self):
        self.listen(EventName.every)
        helm = Helm(self.exchange, self.sensors,self.steerer,self.logger, HELM_CONFIG)

        repeating_steer_event = self.events[EventName.every][1]
        self.assertEqual(repeating_steer_event.next_event.name,EventName.steer)
        self.assertEqual(repeating_steer_event.seconds,3)

    def test_check_course_should_not_steer_if_we_are_turning(self):
        self.helm.turning = True

        self.helm.check_course(Event(EventName.steer))

        self.assertEqual(self.steerer.steer.call_count,0)
