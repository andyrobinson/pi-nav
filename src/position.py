class Position():
    def __init__(self,latitude,longitude, lat_error = 0, long_error = 0):
        self.latitude = latitude
        self.longitude = longitude
        self.lat_error = lat_error
        self.long_error = long_error