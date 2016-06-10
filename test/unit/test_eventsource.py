from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call

from event_source import EventSource
from events import Exchange,Event,EventName

CONFIG = {'tick interval':0.2}

class TestEventSource(unittest.TestCase):

    def setUp(self):
        self.mock_logger = Mock()
        self.exchange = Exchange(self.mock_logger)
        self.timer = Mock()
        self.last_event = None

    def event_recorder(self,event):
        self.last_listened_event = event
        self.event_count += 1

    def intercept_publish(self,event):
        self.exchange.original_publish(event)
        if event.name == EventName.tick:
            raise RuntimeError("oops")

    def listen(self,event_name):
        self.event_count = 0
        self.exchange.subscribe(event_name,self.event_recorder)

    def after(self,times,event_name):
        self.ticks_left = times
        self.end_event_name = event_name

    def count_down_ticks(self,args):
        self.ticks_left -= 1
        if self.ticks_left <= 0:
            self.exchange.publish(Event(self.end_event_name))

    def finish(self,args):
        self.exchange.publish(Event(EventName.end))

    def test_should_publish_start_navigation_event(self):
        self.listen(EventName.start)
        self.timer.wait_for = Mock(side_effect=self.finish)

        event_source = EventSource(self.exchange,self.timer, self.mock_logger,CONFIG)
        event_source.start()

        self.assertEqual(self.last_listened_event.name,EventName.start)

    def test_should_publish_a_tick_event(self):
        self.listen(EventName.tick)
        self.timer.wait_for = Mock(side_effect=self.finish)

        event_source = EventSource(self.exchange, self.timer, self.mock_logger, CONFIG)
        event_source.start()

        self.assertEqual(self.last_listened_event.name,EventName.tick)

    def test_should_publish_multiple_events_until_nav_complete(self):
        self.listen(EventName.tick)
        self.after(5,EventName.end)
        self.timer.wait_for = Mock(side_effect=self.count_down_ticks)

        event_source = EventSource(self.exchange,self.timer, self.mock_logger,CONFIG)
        event_source.start()

        self.assertEqual(self.event_count,5)

    def test_errors_should_be_logged_and_events_continue(self):
        self.listen(EventName.tick)
        self.after(2,EventName.end)
        self.timer.wait_for = Mock(side_effect=self.count_down_ticks)

        self.exchange.original_publish = self.exchange.publish
        self.exchange.publish = self.intercept_publish

        event_source = EventSource(self.exchange,self.timer, self.mock_logger,CONFIG)
        event_source.start()

        self.mock_logger.error.assert_has_calls([call('EventSource, RuntimeError: oops')])
        self.assertEqual(self.event_count,2)

    def test_errors_during_logging_should_be_ignored_and_event_processing_continues(self):
        failing_logger = Mock()
        failing_logger.configure_mock(**{'error.side_effect': RuntimeError})

        self.listen(EventName.tick)
        self.after(2,EventName.end)
        self.timer.wait_for = Mock(side_effect=self.count_down_ticks)

        self.exchange.original_publish = self.exchange.publish
        self.exchange.publish = self.intercept_publish

        event_source = EventSource(self.exchange,self.timer, failing_logger,CONFIG)
        event_source.start()

        failing_logger.error.assert_has_calls([call('EventSource, RuntimeError: oops')])
        self.assertEqual(self.event_count,2)
