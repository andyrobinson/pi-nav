class StubTimer():
    def every(self,seconds):
        self.seconds = seconds

    def call(self,method, *args):
        self.method = method
        self.args = args
        return self
    
    def signal_time_elapsed(self):
        self.method(*self.args)