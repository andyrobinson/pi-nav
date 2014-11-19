import time

class Timer():
    def call(self,method, *args):
        self.method = method
        self.args = args
        return self
    
    def every(self,seconds):
        if not hasattr(self, 'method'):
            raise(RuntimeError("Callback is not defined"))
        
        while self.method(*self.args):
            time.sleep(seconds)
