from setup_test import setup_test
setup_test()

import sys
import unittest
import logging
from events import Exchange,EventName,Event

def test_logger(log_level):
    logging.basicConfig(format='%(asctime)s,%(levelname)s,%(message)s')
    logger = logging.getLogger("test")
    logger.setLevel(log_level)
    return logger

def percentage_diff(original,to_compare):
    return abs(to_compare-original)*100/abs(original)

class EventTestCase(unittest.TestCase):

    def setUp(self):
        self.last_event = Event("None")
        self.events = {}
        self.exchange = Exchange(test_logger(logging.ERROR))

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
