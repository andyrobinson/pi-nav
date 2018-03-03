from setup_test import setup_test
setup_test()

import unittest
from mock import Mock, call, PropertyMock
from copy import deepcopy
from test_utils import EventTestCase
from nan import NaN
from utils.stub_gps import StubGPS
from events import Event, EventName

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
    print 'angle: ' + str(angle)

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
    self.helm.previous_heading = 180

  def deviation(self,heading):
    return abs(self.sensors.compass_heading_average-heading)

  def currently_tracking(self,previous_heading, current_track, rudder_angle=0):
    self.sensors.compass_heading_smoothed = current_track
    self.sensors.compass_heading_average = NaN
    self.sensors.rate_of_turn = current_track - previous_heading
    self.sensors.rate_of_turn_average = self.sensors.rate_of_turn

  def test_it_should_converge_on_requested_heading(self):
    target_heading = 90
    previous_deviation = 90
    self.currently_tracking(180,180)
    self.sensors.compass_heading_average = 180

    self.sensors.log_values(Event(EventName.log_position))

    self.exchange.publish(Event(EventName.set_course,heading=target_heading))

    while (self.deviation(target_heading) > STEERER_CONFIG['ignore deviation below']):
        if (self.rudder_servo.get_position <> 0):
          self.compass.bearing = self.compass.bearing + self.rudder_servo.get_position() * 0.5
          self.exchange.publish(Event(EventName.tick)) # for compass smoothing!
          self.exchange.publish(Event(EventName.update_averages))

        self.sensors.log_values(Event(EventName.log_position))
        self.exchange.publish(Event(EventName.steer))
        self.assertGreater(previous_deviation, self.deviation(target_heading))
        previous_deviation = self.deviation(target_heading)

  def ignore_it_should_converge_on_requested_heading_when_rudder_highly_effective(self):
    pass

  def ignore_it_should_converge_on_requested_heading_when_rudder_ineffective(self):
    pass

  def ignore_it_should_converge_on_requested_heading_with_random_jitter(self):
    pass

  def ignore_it_should_correct_course_deviations_when_originally_on_course(self):
    pass
