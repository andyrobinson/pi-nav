import datetime

class App():
    def __init__(self,logger, gps, timed_callback):
        self.logger = logger
        self.gps = gps
        self.timed_callback = timed_callback

    def track(self, seconds_between_entries):
        self.logger.message('Pi-Nav starting ' + datetime.datetime.now().strftime("%Y-%m-%d"))
        self.timed_callback.call(self.log_position, self.gps).every(seconds_between_entries)
    
    def log_position(self,gps):
        self.logger.info('{:+f},{:+f},{:+f},{:+f}'.format(gps.position.latitude,gps.position.longitude,gps.speed,gps.heading))
        return True
