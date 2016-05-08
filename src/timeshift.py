from events import Event,EventName

class TimeShift:

    def __init__(self,exchange,time):
        self.exchange = exchange
        self.pending_events = {}
        self.time = time
        exchange.subscribe(EventName.after,self._register_event)
        exchange.subscribe(EventName.tick,self._fire_past_events)

    def _fire_past_events(self,tick_event):
        current_time = self.time()
        events_to_fire = dict((time_to_fire, event) for time_to_fire, event in self.pending_events.iteritems() if time_to_fire < current_time)
        for time_to_fire,event in events_to_fire.iteritems():
            self.exchange.publish(event)
            del self.pending_events[time_to_fire]

    def _register_event(self,after_event):
        self.pending_events[self.time() + after_event.seconds] = after_event.next_event
