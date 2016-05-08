from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call
import logging

from timeshift import TimeShift
from events import Exchange,EventName,Event

class EventTest(unittest.TestCase):

    def setUp(self):
        self.last_event = Event("None")
        self.events = {}
        logging.basicConfig(format='%(asctime)s,%(levelname)s,%(message)s', level=logging.ERROR)
        self.exchange = Exchange(logging.getLogger("test"))

    def event_recorder(self,event):
        self.last_event = event
        self.events[event.name].append(event)

    def listen(self,event_name):
        self.events[event_name] = []
        self.exchange.subscribe(event_name,self.event_recorder)

    def event_count(self,event_name):
        if event_name in self.events:
            return len(self.events[event_name])
        else:
            return 0

class TestTimeShift(EventTest):

    def setUp(self):
        super(TestTimeShift, self).setUp()

    def test_should_not_fire_event_on_tick_if_its_not_yet_time(self):
        self.listen(EventName.start)
        mock_time = Mock(side_effect=[145.6, 146.4])
        timeshift = TimeShift(self.exchange,mock_time)

        self.exchange.publish(Event(EventName.after,seconds = 3,next_event=Event(EventName.start)))
        self.exchange.publish(Event(EventName.tick))
        self.assertEqual(self.event_count(EventName.start),0,"start should not have been called")

    def test_should_fire_event_on_tick_if_its_past_its_time(self):
        self.listen(EventName.start)
        mock_time = Mock(side_effect=[145.6, 155.4])
        timeshift = TimeShift(self.exchange,mock_time)

        self.exchange.publish(Event(EventName.after,seconds = 5,next_event=Event(EventName.start)))
        self.exchange.publish(Event(EventName.tick))

        self.assertEqual(self.event_count(EventName.start),1,"start should have been called")
        self.assertEqual(self.last_event.name,EventName.start)

    def test_should_only_fire_events_once(self):
        self.listen(EventName.start)
        mock_time = Mock(side_effect=[145.6, 155.4, 166.2])
        timeshift = TimeShift(self.exchange,mock_time)

        self.exchange.publish(Event(EventName.after,seconds = 5,next_event=Event(EventName.start)))
        self.exchange.publish(Event(EventName.tick))
        self.exchange.publish(Event(EventName.tick))

        event_count = self.event_count(EventName.start)
        self.assertEqual(event_count,1,"start should have been called once, but was called {0} times".format(event_count))

    def test_should_be_able_to_keep_and_fire_multiple_events(self):
        self.listen(EventName.start)
        self.listen(EventName.navigate)

        # Note that time() is called on register, then on tick, awkwardness only during test
        mock_time = Mock(side_effect=[145.6, 145.6, 155.4, 166.2])
        timeshift = TimeShift(self.exchange,mock_time)

        self.exchange.publish(Event(EventName.after,seconds = 5,next_event=Event(EventName.start)))
        self.exchange.publish(Event(EventName.after,seconds = 10,next_event=Event(EventName.navigate)))

        self.exchange.publish(Event(EventName.tick))
        self.assertEqual(self.event_count(EventName.start),1)
        self.assertEqual(self.event_count(EventName.navigate),0)

        self.exchange.publish(Event(EventName.tick))
        self.assertEqual(self.event_count(EventName.navigate),1)
