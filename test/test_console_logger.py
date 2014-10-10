from setup_test import setup_test
setup_test()

import unittest
from datetime import datetime 
from mock import Mock
from StringIO import StringIO

from console_logger import Logger

class TestConsoleLogger(unittest.TestCase):

    def setUp(self):
        self.stdout_double = StringIO()
        self.logger = Logger(self.stdout_double)

    def logged(self):
        return self.stdout_double.getvalue().strip()

    def test_message_should_log_bare_message_to_stdout(self):        
        self.logger.message('test output')
        self.assertEqual(self.logged(),'test output')

    def test_message_should_log_message_only(self):
        self.logger.info('test output')
        self.assertTrue(self.logged().endswith('test output'))
        
    def test_info_should_log_message_with_date(self):
        self.logger.info('xxx')

        log_date = datetime.strptime(self.logged()[:16],"%Y-%m-%d %H:%M")
        self.assertEqual((datetime.now() - log_date).days,0)
        

