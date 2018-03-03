from setup_test import setup_test
setup_test()

import unittest
from mock import Mock, call, PropertyMock
from copy import deepcopy
from test_utils import EventTestCase
from nan import NaN
from utils.stub_gps import StubGPS
from events import Event, EventName
from bearing import to_360

from sensors import Sensors
from helm import Helm
from steerer import Steerer

STEERER_CONFIG = {'full rudder deflection': 30,'ignore deviation below': 5,'ignore rate of turn below': 10,'rate of turn factor': 0.1,'deviation factor': 0.5}
HELM_CONFIG = {'on course threshold': 20,'turn on course min count': 3,'on course check interval': 3,'turn steer interval': 3}
SENSOR_CONFIG = {'smoothing' : 2,'compass smoothing': 2,'log interval': 15, 'update averages interval': 0.2}

class RudderSimulator:
  def __init__(self):
    self.angle = 0

  def set_position(self,angle):
    self.angle = angle

  def get_position(self):
    return self.angle

class TestLogger:
  def debug(self,msg):
    print 'DEBUG ' + msg
  def info(self,msg):
    print 'INFO ' + msg

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

    self.logger = TestLogger()
    self.sensors = Sensors(self.gps,self.windsensor,self.compass,self.mock_time,self.exchange,self.logger,SENSOR_CONFIG)
    self.rudder_servo = RudderSimulator()
    self.steerer = Steerer(self.rudder_servo,self.logger,STEERER_CONFIG)
    self.helm = Helm(self.exchange, self.sensors,self.steerer,self.logger, HELM_CONFIG)
    self.helm.previous_heading = 0

  def deviation(self,heading):
    return abs(self.sensors.compass_heading_average-heading)

  def rotate_boat(self,rudder_effect):
    self.compass.bearing = to_360(self.compass.bearing - self.rudder_servo.get_position() * rudder_effect)
    self.exchange.publish(Event(EventName.tick)) # for compass smoothing!
    self.exchange.publish(Event(EventName.update_averages))

  def test_it_should_converge_on_requested_heading(self):
    target_heading = 90
    previous_deviation = 90

    self.sensors.log_values(Event(EventName.log_position))
    self.exchange.publish(Event(EventName.set_course,heading=target_heading))

    while (self.deviation(target_heading) > STEERER_CONFIG['ignore deviation below'] or abs(self.rudder_servo.get_position()) > 5):
      self.rotate_boat(0.5)
      self.sensors.log_values(Event(EventName.log_position))
      self.exchange.publish(Event(EventName.steer))
      self.assertGreater(previous_deviation, self.deviation(target_heading))
      previous_deviation = self.deviation(target_heading)

    self.sensors.log_values(Event(EventName.log_position))
    print('rudder position on completion ' + str(self.rudder_servo.get_position()))

  def ignore_it_should_converge_on_requested_heading_when_rudder_highly_effective(self):
    pass

  def ignore_it_should_converge_on_requested_heading_when_rudder_ineffective(self):
    pass

  def ignore_it_should_converge_on_requested_heading_with_random_jitter(self):
    pass

  def ignore_it_should_correct_course_deviations_when_originally_on_course(self):
    pass
