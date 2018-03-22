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

class TestHelm(EventTestCase):

    def setUp(self):
        super(TestHelm, self).setUp()
        self.sensors = Mock()
        self.logger = Mock()
        self.steerer = Mock()
        self.helm = Helm(self.exchange, self.sensors,self.steerer,self.logger, HELM_CONFIG)
        self.helm.previous_heading = 180

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
        self.averagely_tracking(204,200)
        self.steerer.on_course.side_effect = [False,False]
        self.exchange.publish(Event(EventName.set_course,heading=196))
        self.steerer.steer.assert_called_with(196,200,-4)

        self.averagely_tracking(200,202)
        self.sensors.rate_of_turn_average = -20
        self.exchange.publish(Event(EventName.check_course))
        self.steerer.steer.assert_called_with(196,202,-20)

    def test_should_not_steer_if_steerer_says_we_are_on_course(self):
        self.averagely_tracking(300,290)
        self.steerer.on_course.side_effect = [True]
        self.exchange.publish(Event(EventName.set_course,heading=294))

        self.assertEqual(self.steerer.steer.call_count,0)

    def test_should_steer_if_off_course_by_more_than_configured_20_degrees(self):
        self.helm.requested_heading = 90
        self.averagely_tracking(50,60)
        self.steerer.on_course.side_effect = [False]

        self.helm.check_course(Event(EventName.check_course))

        self.steerer.steer.assert_called_with(90,60,10)

    def test_should_subscribe_check_course_every_10_seconds(self):
        self.listen(EventName.every)
        helm = Helm(self.exchange, self.sensors,self.steerer,self.logger, HELM_CONFIG)

        self.assertEqual(self.events[EventName.every][0].next_event.name,EventName.check_course)

if __name__ == '__main__':
    unittest.main()
