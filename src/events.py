class Event:
    def __init__(self,name):
        self.name = name

class Exchange:

    def __init__(self):
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
        for callback in self.register[event.name]:
            callback(event)

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
