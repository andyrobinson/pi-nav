import datetime

class Tracker():
    def __init__(self,logger, sensors, timer):
        self.logger = logger
        self.sensors = sensors
        self.timer = timer

    def track(self, seconds_between_entries):
        self.logger.info('Pi-Nav starting ' + datetime.datetime.now().strftime("%Y-%m-%d"))
        self.logger.info('latitude, longitute, +-lat, +-long, speed, track, +-speed, +-track, |, wind, avg wind, abs wind, |, comp, avg comp')
        self.timer.call(self.log_position).every(seconds_between_entries)

    def log_position(self):
        self.sensors.update_averages(None)
        self.sensors.log_values(None)
        return True
