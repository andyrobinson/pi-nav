from nan import isNaN
from position import Position
from events import EventName
from bearing import moving_avg

DEFAULT_ERROR = 10

class Sensors():
    def __init__(self,gps,windsensor,exchange,config):
        self.gps = gps
        self.exchange = exchange
        self.windsensor = windsensor
        self._position = Position(gps.position.latitude,gps.position.longitude)
        self.config = config
        self._wind_relative = 0.0
        exchange.subscribe(EventName.tick,self.update_averages)

    @property
    def hasfix(self):
        return self.gps.hasfix

    @property
    def position(self):
        self._position.latitude = self.gps.position.latitude
        self._position.longitude = self.gps.position.longitude
        self._position.lat_error = self._default(self.gps.position.lat_error,DEFAULT_ERROR)
        self._position.long_error = self._default(self.gps.position.long_error,DEFAULT_ERROR)
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
        return self.windsensor.angle()

    @property
    def wind_direction_relative_average(self):
        return self._wind_relative

    def update_averages(self,tick_event):
        self._wind_relative = moving_avg(self._wind_relative,self.windsensor.angle(),self.config['smoothing'])

    def _default(self,  value,default):
        return default if isNaN(value) else value
