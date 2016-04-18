class Event:
    tick = 1
    start = 2
    end = 3
    navigate = 4
    arrived = 5

    def __init__(self,name,waypoint = None):
        self.name = name
        self.waypoint = waypoint

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
                callback(event)
        else:
            self.logger.warn("Event({}) published but no subscribers".format(event.name))

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
