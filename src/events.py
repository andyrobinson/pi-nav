import sys

class EventName:
    tick = "tick"
    start = "start"
    end = "end"
    navigate = "navigate"
    navigate_review = "navigate_review"
    arrived = "arrived"
    steer = "steer"

class Event:
    def __init__(self,name,waypoint = None, heading = None):
        self.name = name
        self.waypoint = waypoint
        self.heading = heading

class Exchange:

    def __init__(self, logger):
        self.logger = logger
        self.register = {}
        self.events = []
        self.processing = False

    def subscribe(self,name,callback):
        if name in self.register:
            self.register[name].append(callback)
        else:
            self.register[name] = [callback]

    def publish(self,event):
        self.events.append(event)
        if not(self.processing):
            self._process_events()

    def _send_event(self,event):
        if event.name in self.register:
            for callback in self.register[event.name]:
                self._safely_callback(callback,event)
        else:
            self.logger.warn("Event({}) published but no subscribers".format(event.name))

    def _safely_callback(self,callback,event):
        try:
            callback(event)
        except(KeyboardInterrupt):
            quit()
        except:
            try:
                etype,e,traceback = sys.exc_info()
                self.logger.error('Exchange, {0}: {1}'.format(etype.__name__,', '.join(str(x) for x in e.args)))
                self.logger.error('Caused by event {0}, callback {1}'.format(event.name,str(callback)))
            except:
                pass

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
