class StubTimedCallback():
    def __init__(self):
        self.seconds = 0
        self.method = None
        self.args = ()

    def every(self,seconds):
        self.seconds = seconds
        return self

    def call(self,method, *args):
        self.method = method
        self.args = args
        return self
    
    def signal_time_elapsed(self):
        self.method(self.args)