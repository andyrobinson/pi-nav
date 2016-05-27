from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call
from events import Event,Exchange

class TestSubscriber:

    def __init__(self,exchange=None):
        self.event_count = {}
        self.last_event_called = Event("nil")
        self.exchange = exchange

    def callme(self,event):
        self.last_event_called = event
        self._count_event(event)
        if event.name == "chain":
            self.exchange.publish(Event("secondevent"))

    def bad_call(self,event):
        raise RuntimeError('oops')

    def event_call_count(self,name):
        return self.event_count[name]

    def last_event_called(self,event_name):
        return self.last_event_called

    def _count_event(self,event):
        if event.name in self.event_count:
            self.event_count[event.name] = self.event_count[event.name] + 1
        else:
            self.event_count[event.name] = 1

    def raise_event(self,name):
        self.exchange.signal_secondary_event(name)

class TestEvents(unittest.TestCase):
    def setUp(self):
        self.mock_logger = Mock()
        self.exchange = Exchange(self.mock_logger)

    def test_should_return_nil_event_if_not_called(self):
        ts = TestSubscriber()
        self.assertEqual(ts.last_event_called.name,"nil")

    def test_should_call_back(self):
        ts = TestSubscriber(self.exchange)

        self.exchange.subscribe("thing",ts.callme)
        self.exchange.publish(Event("thing"))

    def test_should_ignore_events_with_no_subscribers_and_log_warning(self):
        self.exchange.publish(Event("doesnotexist"))
        self.mock_logger.warn.assert_called_with("Event(doesnotexist) published but no subscribers")

    def test_should_signal_events_to_multiple_subscribers(self):
        ts1 = TestSubscriber(self.exchange)
        ts2 = TestSubscriber(self.exchange)

        self.exchange.subscribe("boo",ts1.callme)
        self.exchange.subscribe("boo",ts2.callme)
        self.exchange.publish(Event("boo"))

        self.assertEqual(ts1.last_event_called.name,"boo")
        self.assertEqual(ts2.last_event_called.name,"boo")

    def test_should_be_able_to_chain_events(self):
        ts1 = TestSubscriber(self.exchange)
        ts2 = TestSubscriber(self.exchange)

        self.exchange.subscribe("chain",ts1.callme)
        self.exchange.subscribe("secondevent",ts2.callme)
        self.exchange.publish(Event("chain"))

        self.assertEqual(ts2.last_event_called.name,"secondevent")

    def test_should_chain_a_few_events(self):
        ts = TestSubscriber(self.exchange)
        ts2 = TestSubscriber(self.exchange)

        self.exchange.subscribe("chain",ts.callme)
        self.exchange.subscribe("secondevent",ts.callme)
        self.exchange.subscribe("secondevent",ts2.callme)
        self.exchange.publish(Event("chain"))

        self.assertEqual(ts.event_call_count("secondevent"),1)
        self.assertEqual(ts2.event_call_count("secondevent"),1)

    def test_should_call_events_again_if_we_signal_primary_event_again(self):
        ts = TestSubscriber(self.exchange)
        event = Event("bing")
        self.exchange.subscribe("bing",ts.callme)
        self.exchange.publish(event)
        self.exchange.publish(event)
        self.exchange.publish(event)

        self.assertEqual(ts.event_call_count("bing"),3)

    def test_errors_should_be_logged_and_event_processing_continues(self):
        ts_error = TestSubscriber(self.exchange)
        ts_after_error = TestSubscriber(self.exchange)
        event = Event("bong")
        self.exchange.subscribe("bong",ts_error.bad_call)
        self.exchange.subscribe("bong",ts_after_error.callme)

        self.exchange.publish(event)

        self.mock_logger.error.assert_has_calls([call('Exchange, RuntimeError: oops')])
        self.assertEqual(ts_after_error.event_call_count("bong"),1)

    def test_errors_during_logging_should_be_ignored_and_event_processing_continues(self):
        failing_logger = Mock()
        failing_logger.configure_mock(**{'error.side_effect': RuntimeError})

        exchange = Exchange(failing_logger)
        ts_error = TestSubscriber(exchange)
        ts_after_error = TestSubscriber(exchange)

        event = Event("bong")
        exchange.subscribe("bong",ts_error.bad_call)
        exchange.subscribe("bong",ts_after_error.callme)

        exchange.publish(event)

        failing_logger.error.assert_has_calls([call('Exchange, RuntimeError: oops')])
        self.assertEqual(ts_after_error.event_call_count("bong"),1)
