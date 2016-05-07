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

  def test_should_fire_event_past_its_delay_on_tick(self):
    self.listen(EventName.start)
    timeshift = TimeShift(self.exchange)

    self.exchange.publish(Event(EventName.after,seconds = 0,next_event=Event(EventName.start)))
    self.exchange.publish(Event(EventName.tick))

    self.assertEqual(self.last_event.name,EventName.start)
