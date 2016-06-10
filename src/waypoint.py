from position import Position

class Waypoint():
    def __init__(self,position,tolerance):
        self.position = position
        self.tolerance = tolerance
        self.longitude = position.longitude
        self.latitude = position.latitude

    def __repr__(self):
        return "{:+.5f},{:+.5f}".format(self.latitude,self.longitude)
