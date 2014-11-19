from setup_test import setup_test
setup_test()

from datetime import datetime
import unittest
from mock import Mock

from timer import Timer
   
class TestTimer(unittest.TestCase):
    def test_callback_given_method_with_arguments(self):
        test_object = Mock(**{'test_method.return_value' : False})

        Timer().call(test_object.test_method,1,2,3).every(0)

        test_object.test_method.assert_called_with(1,2,3)

    def test_callback_waits_for_given_number_of_seconds_between_calls(self):
        test_object = Mock()
        test_object.test_method.side_effect = [True,False]
        start = datetime.now()

        Timer().call(test_object.test_method,1,2,3).every(0.1)

        self.assertEqual(round(float((datetime.now() - start).microseconds)/1000000,1),0.1)
        
    def test_callback_only_runs_once_if_callback_returns_false(self):
        test_object = Mock()
        test_object.test_method.side_effect = [False]
        
        Timer().call(test_object.test_method).every(0)

        self.assertEqual(test_object.test_method.call_count,1)

    def test_callback_runs_repeatedly_until_callback_returns_false(self):
        test_object = Mock()
        test_object.test_method.side_effect = [True,True,False]

        Timer().call(test_object.test_method).every(0)

        self.assertEqual(test_object.test_method.call_count,3)

    def test_callback_flags_error_if_every_called_without_callback(self):
        self.assertRaises(RuntimeError, Timer().every,0)
        
    def test_waitfor_waits_for_the_amount_of_time_specified(self):
        start = datetime.now()

        Timer().wait_for(0.1)

        self.assertEqual(round(float((datetime.now() - start).microseconds)/1000000,1),0.1)
