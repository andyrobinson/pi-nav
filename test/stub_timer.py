class StubTimer():

    def __init__(self):
        self._time = 1000

    def every(self,seconds):
        self.seconds = seconds

    def call(self,method, *args):
        self.method = method
        self.args = args
        return self

    def wait_for(self,seconds):
        self._time += seconds

    def signal_time_elapsed(self):
        self._time += self.seconds
        self.method(*self.args)

    def time(self):
        return self._time
