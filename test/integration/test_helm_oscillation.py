from setup_test import setup_test
setup_test()

import unittest
from random import randint
from mock import Mock, call, PropertyMock
from copy import deepcopy
from test_utils import EventTestCase,test_logger
from nan import NaN
from utils.stub_gps import StubGPS
from events import Event, EventName
from bearing import to_360,angle_between

from sensors import Sensors
from helm import Helm
from steerer import Steerer

STEERER_CONFIG = {'full rudder deflection': 30,'ignore deviation below': 5,'ignore rate of turn below': 10,'rate of turn factor': 0.6,'deviation factor': 0.5}
HELM_CONFIG = {'on course threshold': 20,'turn on course min count': 3,'on course check interval': 3,'turn steer interval': 3}
SENSOR_CONFIG = {'smoothing' : 2,'compass smoothing': 2,'log interval': 15, 'update averages interval': 0.2}

class RudderSimulator:
  def __init__(self):
    self.angle = 0

  def set_position(self,angle):
    self.angle = angle

  def get_position(self):
    return self.angle

class TestHelmOscillation(EventTestCase):

  def mock_time(self):
    return self.time

  def setUp(self):
    super(TestHelmOscillation, self).setUp()

    # Sensors
    mock_angle = PropertyMock(return_value=3.0)
    self.time = 0
    self.gps = StubGPS()
    self.windsensor = Mock()
    self.compass = Mock()
    self.compass.bearing = 0
    type(self.windsensor).angle = mock_angle

    self.logger = Mock()
    self.sensors = Sensors(self.gps,self.windsensor,self.compass,self.mock_time,self.exchange,self.logger,SENSOR_CONFIG)
    self.rudder_servo = RudderSimulator()
    self.steerer = Steerer(self.rudder_servo,self.logger,STEERER_CONFIG)
    self.helm = Helm(self.exchange, self.sensors,self.steerer,self.logger, HELM_CONFIG)
    self.helm.previous_heading = 0

  def deviation(self,heading,jitter):
    return abs(abs(angle_between(self.sensors.compass_heading_smoothed,heading)) - jitter)

  def rotate_boat(self,rudder_effect,jitter):
    self.compass.bearing = to_360(self.compass.bearing + randint(-jitter,jitter) - self.rudder_servo.get_position() * rudder_effect)
    self.time += 0.2
    self.exchange.publish(Event(EventName.tick)) # for compass smoothing!
    self.exchange.publish(Event(EventName.update_averages))

  def set_initial_heading(self,heading):
    self.compass.bearing = heading
    self.sensors._compass_smoothed = heading

  def assert_course_converges(self,target_heading,rudder_effect,jitter=0):
    previous_deviation = self.deviation(target_heading,0)
    deviation_list = [previous_deviation]

    while (self.deviation(target_heading,jitter) > STEERER_CONFIG['ignore deviation below'] or \
            (abs(self.rudder_servo.get_position()) > 5) and self.sensors.rate_of_turn > STEERER_CONFIG['ignore rate of turn below']):
      self.rotate_boat(rudder_effect,jitter)
      self.exchange.publish(Event(EventName.steer))
      deviation_list.append(round(self.deviation(target_heading,jitter),1))
      self.assertGreater(previous_deviation + jitter, self.deviation(target_heading,jitter),"WARNING: RANDOM VALUES IN TEST.  Expected deviation from course to decrease every iteration, but got list " + str(deviation_list))
      previous_deviation = self.deviation(target_heading,0)

  def assert_turn_converges_with_rudder_effect(self, new_heading, rudder_effect, jitter=0):
    self.exchange.publish(Event(EventName.set_course,heading=new_heading))
    self.assert_course_converges(new_heading,rudder_effect,jitter)

  def test_it_should_converge_on_requested_heading_when_rudder_highly_effective(self):
    self.set_initial_heading(90)
    self.assert_turn_converges_with_rudder_effect(180, 0.8)

  def test_it_should_converge_on_requested_heading_when_rudder_ineffective(self):
    self.set_initial_heading(300)
    self.assert_turn_converges_with_rudder_effect(230, 0.1)

  def test_it_should_converge_on_requested_heading_with_random_jitter(self):
    self.set_initial_heading(10)
    self.assert_turn_converges_with_rudder_effect(110, 0.3, 10)

  def test_it_should_converge_on_heading_after_going_off_course(self):
    self.set_initial_heading(110)
    self.assert_turn_converges_with_rudder_effect(110, 0.5)

    self.set_initial_heading(180)
    self.exchange.publish(Event(EventName.check_course))
    self.assert_course_converges(180,0.5)
