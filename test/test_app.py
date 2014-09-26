from setup_test import setup_test
setup_test()

import unittest
from unittest.mock import Mock
import datetime
from main import App

class TestApp(unittest.TestCase):
	def test_should_log_welcome_message_on_init(self):
		now = datetime.datetime.now()
		mock_logger = Mock()

		app = App(mock_logger)

		mock_logger.info.assert_called_with('Pi-Nav starting ' + now.strftime("%Y-%m-%d"))


