from position import Position

class FakeGPS():
    def __init__(self):
        self.hasfix = True
        self.position = Position(53.2,-2.3)
        self.heading = 342.0
        self.speed = 7.3
        self.time = 10
