from setup_test import setup_test
setup_test()
from stub_timedcallback import StubTimedCallback

import unittest
from mock import Mock
import datetime

from main import App
from position import Position

class TestApp(unittest.TestCase):
    def test_should_log_welcome_message(self):
        now = datetime.datetime.now()
        mock_logger = Mock()
        mock_gps = Mock(position=Position(0,0))

        App(mock_logger, mock_gps, StubTimedCallback()).track(300)

        mock_logger.message.assert_called_with('Pi-Nav starting ' + now.strftime("%Y-%m-%d"))

    def test_should_pass_interval_to_callback_timer(self):
        stub_callback = StubTimedCallback()

        App(Mock(), Mock(), stub_callback).track(300)

        self.assertEqual(stub_callback.seconds,300)

    def test_should_log_current_position_speed_and_heading_using_callback_every_time_callback_fires(self):
        latitude = 57.4
        longitude = -4.1
        speed = 2.0
        heading = 270.2

        mock_logger = Mock()
        mock_gps = Mock(position=Position(latitude,longitude),speed=speed,heading=heading)
        stub_callback = StubTimedCallback()

        App(mock_logger, mock_gps, stub_callback).track(300)    
    
        stub_callback.signal_time_elapsed()
        stub_callback.signal_time_elapsed()
        stub_callback.signal_time_elapsed()
        mock_logger.info.assert_called_with('{:+f},{:+f},{:+f},{:+f}'.format(latitude,longitude,speed,heading))
        self.assertEqual(mock_logger.info.call_count,3)

    def test_log_method_should_return_true_to_ensure_logging_continues(self):
        mock_gps = Mock(position=Position(0,0),speed=0,heading=0)
        app=App(Mock(), Mock(), Mock())    

        self.assertTrue(app.log_position(mock_gps))