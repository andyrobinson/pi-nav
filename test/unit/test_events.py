from setup_test import setup_test
setup_test()
import unittest
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

    def test_should_return_nil_event_if_not_called(self):
        ts = TestSubscriber()
        self.assertEqual(ts.last_event_called.name,"nil")

    def test_should_call_back(self):
        exchange = Exchange()
        ts = TestSubscriber(exchange)

        exchange.subscribe("thing",ts.callme)
        exchange.publish(Event("thing"))

        self.assertEqual(ts.last_event_called.name,"thing")

    def test_should_signal_events_to_multiple_subscribers(self):
        exchange = Exchange()
        ts1 = TestSubscriber(exchange)
        ts2 = TestSubscriber(exchange)

        exchange.subscribe("boo",ts1.callme)
        exchange.subscribe("boo",ts2.callme)
        exchange.publish(Event("boo"))

        self.assertEqual(ts1.last_event_called.name,"boo")
        self.assertEqual(ts2.last_event_called.name,"boo")

    def test_should_be_able_to_chain_events(self):
        exchange = Exchange()
        ts1 = TestSubscriber(exchange)
        ts2 = TestSubscriber(exchange)

        exchange.subscribe("chain",ts1.callme)
        exchange.subscribe("secondevent",ts2.callme)
        exchange.publish(Event("chain"))

        self.assertEqual(ts2.last_event_called.name,"secondevent")

    def test_should_chain_a_few_events(self):
        exchange = Exchange()
        ts = TestSubscriber(exchange)
        ts2 = TestSubscriber(exchange)

        exchange.subscribe("chain",ts.callme)
        exchange.subscribe("secondevent",ts.callme)
        exchange.subscribe("secondevent",ts2.callme)
        exchange.publish(Event("chain"))

        self.assertEqual(ts.event_call_count("secondevent"),1)
        self.assertEqual(ts2.event_call_count("secondevent"),1)

    def test_should_call_events_again_if_we_signal_primary_event_again(self):
        exchange = Exchange()
        ts = TestSubscriber(exchange)
        event = Event("bing")
        exchange.subscribe("bing",ts.callme)
        exchange.publish(event)
        exchange.publish(event)
        exchange.publish(event)

        self.assertEqual(ts.event_call_count("bing"),3)
