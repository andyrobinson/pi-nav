from events import Event

class EventSource:

    def __init__(self,exchange,timer):
        self.timer = timer
        self.exchange = exchange
        self.ticking = True
        exchange.subscribe(Event.end,self.finish)

    def start(self):
        self.exchange.publish(Event(Event.start))

        while self.ticking:
            self.exchange.publish(Event(Event.tick))
            self.timer.wait_for(0.2)

    def finish(self,event):
        self.ticking = False
