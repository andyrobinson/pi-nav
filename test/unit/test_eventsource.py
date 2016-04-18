from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call

from event_source import EventSource
from events import Exchange,Event

class TestEventSource(unittest.TestCase):

    def setUp(self):
        self.mock_logger = Mock()
        self.exchange = Exchange(self.mock_logger)
        self.timer = Mock()
        self.last_event = None

    def event_recorder(self,event):
        self.last_listened_event = event
        self.event_count += 1

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
        self.exchange.publish(Event(Event.end))

    def test_should_publish_start_navigation_event(self):
        self.listen(Event.start)
        self.timer.wait_for = Mock(side_effect=self.finish)

        event_source = EventSource(self.exchange,self.timer)
        event_source.start()

        self.assertEqual(self.last_listened_event.name,Event.start)

    def test_should_publish_a_tick_event(self):
        self.listen(Event.tick)
        self.timer.wait_for = Mock(side_effect=self.finish)

        event_source = EventSource(self.exchange,self.timer)
        event_source.start()

        self.assertEqual(self.last_listened_event.name,Event.tick)

    def test_should_publish_multiple_events_until_nav_complete(self):
        self.listen(Event.tick)
        self.after(5,Event.end)
        self.timer.wait_for = Mock(side_effect=self.count_down_ticks)

        event_source = EventSource(self.exchange,self.timer)
        event_source.start()

        self.assertEqual(self.event_count,5)
