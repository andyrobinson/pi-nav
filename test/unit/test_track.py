from setup_test import setup_test
setup_test()
from stub_timedcallback import StubTimedCallback

import unittest
from mock import Mock, call
import datetime

from track import Tracker
from position import Position

class TestTrack(unittest.TestCase):
    def test_should_log_welcome_message_and_column_headers(self):
        now = datetime.datetime.now()
        mock_logger = Mock()
        mock_gps = Mock(position=Position(0,0))

        Tracker(mock_logger, mock_gps, StubTimedCallback()).track(300)

        mock_logger.info.assert_has_calls([call('Pi-Nav starting ' + now.strftime("%Y-%m-%d")), 
            call('latitude, longitute, +-lat, +-long, speed, track, +-speed, +-track')])

    def test_should_pass_interval_to_callback_timer(self):
        stub_callback = StubTimedCallback()

        Tracker(Mock(), Mock(), stub_callback).track(300)

        self.assertEqual(stub_callback.seconds,300)

    def test_should_log_current_position_speed_and_track_using_callback_every_time_callback_fires(self):
        latitude = 57.4
        longitude = -4.1
        speed = 2.0
        track = 270.2
        error = 7.3
        number_of_header_lines = 2

        mock_logger = Mock()
        mock_gps = Mock(position=Position(latitude,longitude,error,error),speed=speed,track=track,speed_error=error,track_error=error)
        stub_callback = StubTimedCallback()

        Tracker(mock_logger, mock_gps, stub_callback).track(300)    
    
        stub_callback.signal_time_elapsed()
        stub_callback.signal_time_elapsed()
        stub_callback.signal_time_elapsed()
        mock_logger.info.assert_called_with('{:+f},{:+f},{:+f},{:+f},{:+f},{:+f},{:+f},{:+f}'.format(latitude,longitude,error,error,speed,track,error,error))
        self.assertEqual(mock_logger.info.call_count,3 + number_of_header_lines) 

    def test_log_method_should_return_true_to_ensure_logging_continues(self):
        mock_gps = Mock(position=Position(0,0),speed=0,track=0,speed_error=0,track_error=0)
        tracker=Tracker(Mock(), Mock(), Mock())    

        self.assertTrue(tracker.log_position(mock_gps))