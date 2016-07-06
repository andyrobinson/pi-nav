from setup_test import setup_test

setup_test()

import unittest
from mock import Mock,PropertyMock

from utils.stub_gps import StubGPS
from sensors import Sensors
from nan import NaN
from events import Exchange,EventName,Event
from test_utils import EventTestCase

DEFAULT_CONFIG = {'smoothing' : 2, 'log interval': 15, 'update averages interval': 0.2}

class TestSensors(EventTestCase):
    def mock_time(self):
        return self.time

    @property
    def sensors(self):
        return Sensors(self.gps,self.windsensor,self.compass,self.mock_time,self.exchange,self.logger,DEFAULT_CONFIG)

    def setUp(self):
        mock_angle = PropertyMock(return_value=3.0)
        mock_bearing = PropertyMock(return_value=0.0)
        super(TestSensors, self).setUp()
        self.time = 0
        self.gps = StubGPS()
        self.windsensor = Mock()
        self.compass = Mock()
        self.logger = Mock()
        type(self.compass).bearing = mock_bearing
        type(self.windsensor).angle = mock_angle

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

        sensors = Sensors(gps,Mock(),self.compass,self.mock_time,self.exchange,self.logger,DEFAULT_CONFIG)

        self.assertEqual(sensors.position.lat_error, 10)
        self.assertEqual(sensors.position.long_error, 10)
        self.assertEqual(sensors.speed_error, 10)
        self.assertEqual(sensors.track_error, 10)

    def test_should_register_the_update_averages_event_according_to_config(self):
        self.listen(EventName.every)
        sensors = self.sensors

        update_averages_event = self.events[EventName.every][1]
        self.assertEqual(update_averages_event.next_event.name,EventName.update_averages)
        self.assertEqual(update_averages_event.seconds,DEFAULT_CONFIG['update averages interval'])

    def test_should_pass_through_wind_drection(self):
        mock_angle = PropertyMock(return_value=10.0)
        windsensor = Mock()
        type(windsensor).angle = mock_angle
        sensors = Sensors(StubGPS(),windsensor,self.compass,self.mock_time,self.exchange,self.logger,DEFAULT_CONFIG)
        self.assertEqual(sensors.wind_direction_relative_instant, 10.0)

    def test_should_return_wind_relative_as_zero_initially(self):
        self.assertEqual(self.sensors.wind_direction_relative_average, 0.0)

    def test_should_return_wind_relative_average_after_several_update_averages_events(self):
        mock_angle = PropertyMock(side_effect=[10.0,20.0])
        windsensor = Mock()
        type(windsensor).angle = mock_angle
        sensors = Sensors(StubGPS(),windsensor,self.compass,self.mock_time,self.exchange,self.logger,DEFAULT_CONFIG)
        self.exchange.publish(Event(EventName.update_averages))
        self.exchange.publish(Event(EventName.update_averages))
        self.assertEqual(sensors.wind_direction_relative_average, round(((0.0 + 10)/2 + 20)/2),0)

    def test_should_provide_a_rounded_average_for_values_either_side_of_zero(self):
        mock_angle = PropertyMock(side_effect=[350.0,0.0,10.0])
        windsensor = Mock()
        type(windsensor).angle = mock_angle
        sensors = Sensors(StubGPS(),windsensor,self.compass,self.mock_time,self.exchange,self.logger,DEFAULT_CONFIG)
        self.exchange.publish(Event(EventName.update_averages))
        self.exchange.publish(Event(EventName.update_averages))
        self.exchange.publish(Event(EventName.update_averages))
        self.assertEqual(sensors.wind_direction_relative_average, 4.0)

    def test_should_pass_though_compass_bearing(self):
        mock_bearing = PropertyMock(return_value=57.0)
        compass = Mock()
        type(compass).bearing = mock_bearing
        sensors = Sensors(StubGPS(),self.windsensor,compass,self.mock_time,self.exchange,self.logger,DEFAULT_CONFIG)

        self.assertEqual(sensors.compass_heading_instant,57.0)

    def test_should_return_compass_average_after_several_ticks(self):
        mock_bearing = PropertyMock(side_effect=[10.0,20.0])
        mock_compass = Mock()
        type(mock_compass).bearing = mock_bearing
        sensors = Sensors(StubGPS(),self.windsensor,mock_compass,self.mock_time,self.exchange,self.logger,DEFAULT_CONFIG)
        self.exchange.publish(Event(EventName.update_averages))
        self.exchange.publish(Event(EventName.update_averages))
        self.assertEqual(sensors.compass_heading_average, round(((0.0 + 10)/2 + 20)/2),0)

    def test_should_return_absolute_wind_direction_based_on_rounded_averages(self):
        mock_bearing = PropertyMock(side_effect=[10.0,30.0,50.0])
        mock_compass = Mock()
        type(mock_compass).bearing = mock_bearing
        mock_angle = PropertyMock(side_effect=[0.0,340.0,320.0])
        mock_windsensor = Mock()
        type(mock_windsensor).angle = mock_angle

        sensors = Sensors(StubGPS(),mock_windsensor,mock_compass,self.mock_time,self.exchange,self.logger,DEFAULT_CONFIG)
        self.exchange.publish(Event(EventName.update_averages))
        self.exchange.publish(Event(EventName.update_averages))
        self.exchange.publish(Event(EventName.update_averages))

        self.assertEqual(sensors.wind_direction_abs_average, 9.0)

    def test_should_return_absolute_wind_direction_based_on_rounded_averages_around_zero(self):
        mock_bearing = PropertyMock(side_effect=[345,5.0,20.0])
        mock_compass = Mock()
        type(mock_compass).bearing = mock_bearing
        mock_angle = PropertyMock(side_effect=[10.0,355.0,335.0])
        mock_windsensor = Mock()
        type(mock_windsensor).angle = mock_angle

        sensors = Sensors(StubGPS(),mock_windsensor,mock_compass,self.mock_time,self.exchange,self.logger,DEFAULT_CONFIG)
        self.exchange.publish(Event(EventName.update_averages))
        self.exchange.publish(Event(EventName.update_averages))
        self.exchange.publish(Event(EventName.update_averages))

        self.assertEqual(sensors.wind_direction_abs_average, 357.0)

    def test_should_log_all_sensor_values(self):
        self.logger.reset_mock()
        self.sensors.log_values(Event(EventName.log_position))
        self.logger.info.assert_called_once_with("+53.200000,-2.300000,+0.000000,+0.000000,+7.30,+342.0,+1.00,+2.0,|,+3.0,+0.0,+0.0,|,+0.0,+0.0")

    def test_should_register_logging_according_to_config(self):
        self.listen(EventName.every)
        config = DEFAULT_CONFIG
        config['log interval'] = 15

        sensors = Sensors(self.gps,self.windsensor,self.compass,self.mock_time,self.exchange,self.logger,config)

        every_event = self.events[EventName.every][0]
        self.assertEqual(every_event.seconds,15)
        self.assertEqual(every_event.next_event.name,EventName.log_position)

    def test_should_return_the_rate_of_turn(self):
        mock_bearing = PropertyMock(side_effect=[5.0,10.0,15.0])
        mock_compass = Mock()
        type(mock_compass).bearing = mock_bearing
        time_between_bearing_samples = 0.5

        sensors = Sensors(StubGPS(),self.windsensor,mock_compass,self.mock_time,self.exchange,self.logger,DEFAULT_CONFIG)

        self.time = 1.2
        self.exchange.publish(Event(EventName.update_averages))
        self.time = 1.2 + time_between_bearing_samples
        self.exchange.publish(Event(EventName.update_averages))

        self.assertEqual(5/time_between_bearing_samples,sensors.rate_of_turn)

    def test_should_return_the_average_rate_of_turn(self):
        mock_bearing = PropertyMock(side_effect=[2.0,5.0,8.0,11.0])
        mock_compass = Mock()
        type(mock_compass).bearing = mock_bearing
        time_between_bearing_samples = 1

        sensors = Sensors(StubGPS(),self.windsensor,mock_compass,self.mock_time,self.exchange,self.logger,DEFAULT_CONFIG)

        for i in range(1,5):
            self.time += time_between_bearing_samples
            self.exchange.publish(Event(EventName.update_averages))

        self.assertEqual(2.6875,sensors.rate_of_turn_average)
        self.assertEqual(3,sensors.rate_of_turn)

    def test_should_return_the_average_rate_of_turn_anticlockwise_as_negative(self):
        mock_bearing = PropertyMock(side_effect=[357.0,354.0,351.0,348.0])
        mock_compass = Mock()
        type(mock_compass).bearing = mock_bearing
        time_between_bearing_samples = 1

        sensors = Sensors(StubGPS(),self.windsensor,mock_compass,self.mock_time,self.exchange,self.logger,DEFAULT_CONFIG)

        for i in range(1,5):
            self.time += time_between_bearing_samples
            self.exchange.publish(Event(EventName.update_averages))

        self.assertEqual(-2.71875,sensors.rate_of_turn_average)
        self.assertEqual(-3,sensors.rate_of_turn)
