from position import Position

class StubGPS():
    def __init__(self):
        self.hasfix = True
        self.position = Position(53.2,-2.3)
        self.track = 342.0
        self.speed = 7.3
        self.time = 10
        self.speed_error =1
        self.track_error = 2
