import datetime

class Tracker():
    def __init__(self,logger, gps, timer):
        self.logger = logger
        self.gps = gps
        self.timer = timer

    def track(self, seconds_between_entries):
        self.logger.info('Pi-Nav starting ' + datetime.datetime.now().strftime("%Y-%m-%d"))
        self.logger.info('latitude, longitute, +-lat, +-long, speed, track, +-speed, +-track, |, wind, avg wind, abs wind, |, comp, avg comp')
        self.timer.call(self.log_position, self.gps).every(seconds_between_entries)

    def log_position(self,gps):
        self.logger.info('{:+f},{:+f},{:+f},{:+f},{:+f},{:+f},{:+f},{:+f}'.format(gps.position.latitude,
            gps.position.longitude,gps.position.lat_error, gps.position.long_error,
            gps.speed,gps.track,gps.speed_error,gps.track_error))
        return True
