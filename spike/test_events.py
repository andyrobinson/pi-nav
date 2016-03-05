import unittest
import time

class Event:
    def __init__(self,name):
        self.name = name

class TestSubscriber:

    def __init__(self,exchange=None):
        self.event_count = {}
        self.last_event_called = Event("nil")
        self.exchange = exchange

    def callme(self,event):
        print("EVENT!! " + event.name)
        self.last_event_called = event
        self._count_event(event)
        if event.name == "chain":
            self.raise_event("secondevent")

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

class Exchange:

    def __init__(self):
        self.register = {}
        self.events = []

    def add_subscriber(self,name,callback):
        if name in self.register:
            self.register[name].append(callback)
        else:
            self.register[name] = [callback]

    def signal_event(self,event_name):
        self.events = [Event(event_name)]
        self._process_events()

    def signal_secondary_event(self,event_name):
        if not(event_name in self.events):
            self.events.append(Event(event_name))

    def signal_tick(self):
        self.signal_event("tick")

    def _send_event(self,event):
        for callback in self.register[event.name]:
            callback(event)

    def _process_events(self):
        i = 0
        while i < len(self.events):
            self._send_event(self.events[i])
            i = i + 1

class TestEvents(unittest.TestCase):

    def test_should_return_nil_event_if_not_called(self):
        ts = TestSubscriber()
        self.assertEqual(ts.last_event_called.name,"nil")

    def test_should_call_back(self):
        exchange = Exchange()
        ts = TestSubscriber(exchange)

        exchange.add_subscriber("thing",ts.callme)
        exchange.signal_event("thing")

        self.assertEqual(ts.last_event_called.name,"thing")

    def test_should_signal_clock_tick(self):
        exchange = Exchange()
        ts = TestSubscriber(exchange)

        exchange.add_subscriber("tick",ts.callme)
        exchange.signal_tick()

        self.assertEqual(ts.last_event_called.name,"tick")

    def test_should_signal_ticks_to_multiple_subscribers(self):
        exchange = Exchange()
        ts1 = TestSubscriber(exchange)
        ts2 = TestSubscriber(exchange)

        exchange.add_subscriber("tick",ts1.callme)
        exchange.add_subscriber("tick",ts2.callme)
        exchange.signal_tick()

        self.assertEqual(ts1.last_event_called.name,"tick")
        self.assertEqual(ts2.last_event_called.name,"tick")

    def test_should_be_able_to_chain_events(self):
        exchange = Exchange()
        ts1 = TestSubscriber(exchange)
        ts2 = TestSubscriber(exchange)

        exchange.add_subscriber("chain",ts1.callme)
        exchange.add_subscriber("secondevent",ts2.callme)
        exchange.signal_event("chain")

        self.assertEqual(ts2.last_event_called.name,"secondevent")

    def test_should_only_chain_events_once(self):
        exchange = Exchange()
        ts = TestSubscriber(exchange)

        exchange.add_subscriber("boo",ts.callme)
        exchange.signal_event("boo")
        exchange.signal_secondary_event("boo")

        self.assertEqual(ts.event_call_count("boo"),1)

    def test_should_chain_a_few_events(self):
        exchange = Exchange()
        ts = TestSubscriber(exchange)
        ts2 = TestSubscriber(exchange)

        exchange.add_subscriber("chain",ts.callme)
        exchange.add_subscriber("secondevent",ts.callme)
        exchange.add_subscriber("secondevent",ts2.callme)
        exchange.signal_event("chain")

        self.assertEqual(ts.event_call_count("secondevent"),1)
        self.assertEqual(ts2.event_call_count("secondevent"),1)

    def test_should_call_events_again_if_we_signal_primary_event_again(self):
        exchange = Exchange()
        ts = TestSubscriber(exchange)

        exchange.add_subscriber("bing",ts.callme)
        exchange.signal_event("bing")
        exchange.signal_event("bing")
        exchange.signal_event("bing")

        self.assertEqual(ts.event_call_count("bing"),3)

    # def test_lets_do_something(self):
    #     exchange = Exchange()
    #     ts = TestSubscriber(exchange)
    #
    #     exchange.add_subscriber("tick",ts.callme)
    #
    #     i = 0
    #     while i < 50:
    #         time.sleep(1)
    #         exchange.signal_tick()
    #         i = i+1
