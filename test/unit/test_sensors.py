from setup_test import setup_test

setup_test()

import unittest
from mock import Mock

from utils.stub_gps import StubGPS
from sensors import Sensors
from nan import NaN
from events import Exchange,EventName,Event
from test_utils import EventTestCase

DEFAULT_CONFIG = {'smoothing' : 3}

class TestSensors(EventTestCase):
    def setUp(self):
        super(TestSensors, self).setUp()
        self.gps = StubGPS()
        self.windsensor = Mock()
        self.compass = Mock()
        self.compass.bearing = Mock(return_value = 0.0)
        self.windsensor.angle = Mock(return_value = 0.0)
        self.sensors = Sensors(self.gps,self.windsensor,self.compass,self.exchange,DEFAULT_CONFIG)

    def test_should_pass_through_gps_values(self):
        self.assertEqual(self.sensors.hasfix, self.gps.hasfix)
        self.assertEqual(self.sensors.position.latitude, self.gps.position.latitude)
        self.assertEqual(self.sensors.position.longitude, self.gps.position.longitude)
        self.assertEqual(self.sensors.position.lat_error, self.gps.position.lat_error)
        self.assertEqual(self.sensors.position.long_error, self.gps.position.long_error)
        self.assertEqual(self.sensors.track, self.gps.track)
        self.assertEqual(self.sensors.speed, self.gps.speed)
        self.assertEqual(self.sensors.time, self.gps.time)
        self.assertEqual(self.sensors.speed_error, self.gps.speed_error)
        self.assertEqual(self.sensors.track_error, self.gps.track_error)

    def test_should_reflect_changes_in_gps_values(self):
        self.gps.hasfix = 'blah'
        self.assertEqual(self.sensors.hasfix, 'blah')

    def test_should_default_error_values_to_ten_if_gps_returns_NaN(self):
        gps = StubGPS()
        gps.position.lat_error = NaN
        gps.position.long_error = NaN
        gps.speed_error = NaN
        gps.track_error = NaN

        sensors = Sensors(gps,Mock(),self.compass,self.exchange,DEFAULT_CONFIG)

        self.assertEqual(sensors.position.lat_error, 10)
        self.assertEqual(sensors.position.long_error, 10)
        self.assertEqual(sensors.speed_error, 10)
        self.assertEqual(sensors.track_error, 10)

    def test_should_pass_through_wind_drection(self):
        windsensor = Mock()
        windsensor.angle.side_effect = [10.0,20.0]
        sensors = Sensors(StubGPS(),windsensor,self.compass,self.exchange,DEFAULT_CONFIG)
        self.assertEqual(sensors.wind_direction_relative_instant, 10.0)
        self.assertEqual(sensors.wind_direction_relative_instant, 20.0)

    def test_should_return_wind_relative_as_zero_initially(self):
        self.assertEqual(self.sensors.wind_direction_relative_average, 0.0)

    def test_should_return_wind_relative_average_after_several_ticks(self):
        windsensor = Mock()
        windsensor.angle.side_effect = [10.0,20.0]
        sensors = Sensors(StubGPS(),windsensor,self.compass,self.exchange,{'smoothing' : 2})
        self.exchange.publish(Event(EventName.tick))
        self.exchange.publish(Event(EventName.tick))
        self.assertEqual(sensors.wind_direction_relative_average, round(((0.0 + 10)/2 + 20)/2),0)

    def test_should_provide_a_rounded_average_for_values_either_side_of_zero(self):
        windsensor = Mock()
        windsensor.angle.side_effect = [350.0,0.0,10.0]
        sensors = Sensors(StubGPS(),windsensor,self.compass,self.exchange,{'smoothing' : 2})
        self.exchange.publish(Event(EventName.tick))
        self.exchange.publish(Event(EventName.tick))
        self.exchange.publish(Event(EventName.tick))
        self.assertEqual(sensors.wind_direction_relative_average, 4.0)

    def test_should_pass_though_compass_bearing(self):
        compass = Mock()
        compass.bearing.side_effect = [57.0]
        sensors = Sensors(StubGPS(),self.windsensor,compass,self.exchange,{'smoothing' : 2})

        self.assertEqual(sensors.compass_heading_instant,57.0)

    def test_should_return_compass_average_after_several_ticks(self):
        mock_compass = Mock()
        mock_compass.bearing.side_effect = [10.0,20.0]
        sensors = Sensors(StubGPS(),self.windsensor,mock_compass,self.exchange,{'smoothing' : 2})
        self.exchange.publish(Event(EventName.tick))
        self.exchange.publish(Event(EventName.tick))
        self.assertEqual(sensors.compass_heading_average, round(((0.0 + 10)/2 + 20)/2),0)

    def test_should_return_absolute_wind_direction_based_on_rounded_averages(self):
        mock_compass = Mock()
        mock_compass.bearing.side_effect = [10.0,30.0,50.0]
        mock_windsensor = Mock()
        mock_windsensor.angle.side_effect = [0.0,340.0,320.0]

        sensors = Sensors(StubGPS(),mock_windsensor,mock_compass,self.exchange,{'smoothing' : 2})
        self.exchange.publish(Event(EventName.tick))
        self.exchange.publish(Event(EventName.tick))
        self.exchange.publish(Event(EventName.tick))

        self.assertEqual(sensors.wind_direction_abs_average, 9.0)

    def test_should_return_absolute_wind_direction_based_on_rounded_averages_around_zero(self):
        mock_compass = Mock()
        mock_compass.bearing.side_effect = [345,5.0,20.0]
        mock_windsensor = Mock()
        mock_windsensor.angle.side_effect = [10.0,355.0,335.0]

        sensors = Sensors(StubGPS(),mock_windsensor,mock_compass,self.exchange,{'smoothing' : 2})
        self.exchange.publish(Event(EventName.tick))
        self.exchange.publish(Event(EventName.tick))
        self.exchange.publish(Event(EventName.tick))

        self.assertEqual(sensors.wind_direction_abs_average, 357.0)
