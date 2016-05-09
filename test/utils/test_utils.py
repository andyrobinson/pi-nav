from setup_test import setup_test
setup_test()
import unittest
import logging
from events import Exchange,EventName,Event

def percentage_diff(original,to_compare):
    return abs(to_compare-original)*100/abs(original)

class EventTestCase(unittest.TestCase):

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
