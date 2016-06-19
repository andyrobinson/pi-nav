import sys

class EventName:
    tick = "tick"
    start = "start"
    end = "end"
    navigate = "navigate"
    navigate_review = "navigate review"
    arrived = "arrived"
    set_course = "set course"
    turn = "turn"
    check_course = "check course"
    after = "after"
    every = "every"
    log_position = "log position"

class Event:
    def __init__(self,name,waypoint = None, heading = None, seconds = 0, next_event = None):
        self.name = name
        self.waypoint = waypoint
        self.heading = heading
        self.seconds = seconds
        self.next_event = next_event

    def __repr__(self):
        next_event = self.next_event.name if self.next_event else "None"
        representation = "Event[{}]: waypoint={}, heading={}, secs={},next_event={}".format(self.name,repr(self.waypoint),self.heading,self.seconds,next_event )

        return (representation)


class Exchange:

    def __init__(self, logger):
        self.logger = logger
        self.register = {}
        self.events = []
        self.processing = False

    def subscribe(self,name,callback):
        self.logger.debug("subscribe to event {}, callback {}".format(name,callback))
        if name in self.register:
            self.register[name].add(callback)
        else:
            self.register[name] = set([callback])

    def unsubscribe(self,name,callback):
        self.logger.debug("unsubscribe to event {}, callback {}".format(name,callback))
        if name in self.register:
            self.register[name].remove(callback)

    def publish(self,event):
        self.logger.debug("publishing event " + repr(event))
        self.events.append(event)
        if not(self.processing):
            self._process_events()

    def _send_event(self,event):
        if event.name in self.register and len(self.register[event.name]) > 0:
            immutable_events_to_call = self.register[event.name].copy()
            for callback in immutable_events_to_call:
                self._safely_callback(callback,event)
        else:
            self.logger.warn("Event({}) published but no subscribers".format(event.name))

    def _safely_callback(self,callback,event):
        # try:
        callback(event)
        # except(KeyboardInterrupt):
        #     quit()
        # except:
        #     try:
        #         etype,e,traceback = sys.exc_info()
        #         self.logger.error('Exchange, {0}: {1}'.format(etype.__name__,', '.join(str(x) for x in e.args)))
        #         self.logger.error('Caused by event {0}, callback {1}'.format(event.name,str(callback)))
        #     except:
        #         pass

    def _process_events(self):
        self.processing = True
        i = 0
        while i < len(self.events):
            self._send_event(self.events[i])
            i = i + 1

        self._end_processing()

    def _end_processing(self):
        self.processing = False
        self.events = []

    def __repr__(self):
        return str(self.register)
