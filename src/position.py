class Position():
    def __init__(self, latitude, longitude, lat_error = 0, long_error = 0):
        self.latitude = latitude
        self.longitude = longitude
        self.lat_error = lat_error
        self.long_error = long_error

    def __eq__(self, other):
        return self.latitude == other.latitude and \
            self.longitude == other.longitude and \
            self.lat_error == other.lat_error and \
            self.long_error == other.long_error