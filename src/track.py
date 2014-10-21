import datetime

class Tracker():
    def __init__(self,logger, gps, timed_callback):
        self.logger = logger
        self.gps = gps
        self.timed_callback = timed_callback

    def track(self, seconds_between_entries):
        self.logger.info('Pi-Nav starting ' + datetime.datetime.now().strftime("%Y-%m-%d"))
        self.logger.info('latitude, longitute, +-lat, +-long, speed, track, +-speed, +-track')
        self.timed_callback.call(self.log_position, self.gps).every(seconds_between_entries)
    
    def log_position(self,gps):
        self.logger.info('{:+f},{:+f},{:+f},{:+f},{:+f},{:+f},{:+f},{:+f}'.format(gps.position.latitude,
            gps.position.longitude,gps.position.lat_error, gps.position.long_error,
            gps.speed,gps.track,gps.speed_error,gps.track_error))
        return True
