import datetime

class App():
    def __init__(self,logger, gps, timed_callback):
        self.logger = logger
        self.gps = gps
        self.timed_callback = timed_callback

    def track(self, seconds_between_entries):
        self.logger.message('Pi-Nav starting ' + datetime.datetime.now().strftime("%Y-%m-%d"))
        self.timed_callback.every(seconds_between_entries).call(self.log_position, self.gps)
    
    def log_position(self,gps):
        self.logger.info('{:+f},{:+f}'.format(self.gps.lat,self.gps.long))
