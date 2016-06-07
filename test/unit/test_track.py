from setup_test import setup_test
setup_test()
from stub_timer import StubTimer

import unittest
from mock import Mock, call
import datetime

from track import Tracker
from position import Position
from fake_moving_gps import FakeMovingGPS
from fake_sensors import FakeSensors

class TestTrack(unittest.TestCase):
    def test_should_log_welcome_message_and_column_headers(self):
        now = datetime.datetime.now()
        mock_logger = Mock()
        mock_sensors = Mock()

        Tracker(mock_logger, mock_sensors, StubTimer()).track(300)

        mock_logger.info.assert_has_calls([call('Pi-Nav starting ' + now.strftime("%Y-%m-%d")),
            call('latitude, longitute, +-lat, +-long, speed, track, +-speed, +-track, |, wind, avg wind, abs wind, |, comp, avg comp')])

    def test_should_pass_interval_to_callback_timer(self):
        stub_callback = StubTimer()

        Tracker(Mock(), Mock(), stub_callback).track(300)

        self.assertEqual(stub_callback.seconds,300)

    def test_should_call_update_stats(self):
        stub_callback = StubTimer()
        sensors = Mock()

        Tracker(Mock(), sensors, stub_callback).track(300)
        stub_callback.signal_time_elapsed()

        sensors.update_averages.assert_called_once_with(None)

    def test_should_log_current_position_callback_every_time_callback_fires(self):
        stub_callback = StubTimer()
        sensors = Mock()

        Tracker(Mock(), sensors, stub_callback).track(300)
        stub_callback.signal_time_elapsed()
        stub_callback.signal_time_elapsed()
        stub_callback.signal_time_elapsed()

        self.assertEqual(sensors.log_position.call_count,3)

    def test_log_method_should_return_true_to_ensure_logging_continues(self):
        sensors = Mock()
        tracker=Tracker(Mock(), sensors, Mock())

        self.assertTrue(tracker.log_position())
