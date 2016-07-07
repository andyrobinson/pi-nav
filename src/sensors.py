from nan import isNaN
from position import Position
from events import Event,EventName
from bearing import moving_avg,to_360,angle_between

DEFAULT_ERROR = 10

class Sensors():
    def __init__(self,gps,windsensor,compass,time_fn,exchange,logger,config):
        self.gps = gps
        self.exchange = exchange
        self.windsensor = windsensor
        self.compass = compass
        self.logger = logger
        position = gps.position
        self._position = Position(position.latitude,position.longitude)
        self.config = config
        self._wind_relative_avg = 0.0
        self._compass_avg = 0.0
        self.system_time = time_fn
        self._previous_bearing = 0
        self._previous_time = self.system_time()-1
        self._rate_of_turn = 0
        self._rate_of_turn_average = 0
        exchange.subscribe(EventName.update_averages,self.update_averages)
        exchange.subscribe(EventName.log_position,self.log_values)
        exchange.subscribe(EventName.tick,self.update_compass_bearing)
        exchange.publish(Event(EventName.every,seconds = config['log interval'],next_event = Event(EventName.log_position)))
        exchange.publish(Event(EventName.every,seconds = config['update averages interval'],next_event = Event(EventName.update_averages)))

    @property
    def hasfix(self):
        return self.gps.hasfix

    @property
    def position(self):
        gps_position = self.gps.position
        self._position.latitude = gps_position.latitude
        self._position.longitude = gps_position.longitude
        self._position.lat_error = self._default(gps_position.lat_error,DEFAULT_ERROR)
        self._position.long_error = self._default(gps_position.long_error,DEFAULT_ERROR)
        return self._position

    @property
    def time(self):
        return self.gps.time

    @property
    def track(self):
        return self.gps.track

    @property
    def speed(self):
        return self.gps.speed

    @property
    def track_error(self):
        return self._default(self.gps.track_error,DEFAULT_ERROR)

    @property
    def speed_error(self):
        return self._default(self.gps.speed_error,DEFAULT_ERROR)

    @property
    def wind_direction_relative_instant(self):
        return self.windsensor.angle

    @property
    def wind_direction_relative_average(self):
        return round(self._wind_relative_avg,0)

    @property
    def wind_direction_abs_average(self):
        return round(to_360(self._compass_avg + self._wind_relative_avg),0)

    @property
    def compass_heading_instant(self):
        return self.compass.bearing

    @property
    def compass_heading_average(self):
        return round(self._compass_avg,0)

    @property
    def rate_of_turn(self):
        return self._rate_of_turn

    @property
    def rate_of_turn_average(self):
        return self._rate_of_turn_average

    def update_averages(self,unused_event):
        wind = self.windsensor.angle
        bearing = self.compass.bearing
        smoothing = self.config['smoothing']
        self._wind_relative_avg = moving_avg(self._wind_relative_avg,wind,smoothing)
        self._compass_avg = moving_avg(self._compass_avg,bearing,smoothing)
        self._calculate_rate_of_turn(bearing)
        rate_of_turn_diff = self._rate_of_turn-self._rate_of_turn_average
        self._rate_of_turn_average += rate_of_turn_diff/smoothing

    def update_compass_bearing(self,unused_event):
        pass

    def _calculate_rate_of_turn(self,bearing):
        time_now = self.system_time()
        if time_now <= self._previous_time:
            self._rate_of_turn = 0
        else:
            self._rate_of_turn = angle_between(self._previous_bearing,bearing)/(time_now - self._previous_time)
        self._previous_bearing = bearing
        self._previous_time = time_now

    def log_values(self,unused_event):
        self.logger.info('{:+f},{:+f},{:+f},{:+f},{:+.2f},{:+.1f},{:+.2f},{:+.1f},|,{:+.1f},{:+.1f},{:+.1f},|,{:+.1f},{:+.1f}'.format(
            self.gps.position.latitude,
            self.gps.position.longitude,
            self.gps.position.lat_error,
            self.gps.position.long_error,
            self.gps.speed,
            self.gps.track,
            self.gps.speed_error,
            self.gps.track_error,
            self.wind_direction_relative_instant,
            self.wind_direction_relative_average,
            self.wind_direction_abs_average,
            self.compass_heading_instant,
            self.compass_heading_average))

    def _default(self,  value,default):
        return default if isNaN(value) else value
