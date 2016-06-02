from globe import Globe

class FakeMovingGPS():
    def __init__(self,positions,globe = Globe()):
        self.positions = positions
        self.globe = globe
        self.position_index = 0
        self.wind_direction = 0

    @property
    def position(self):
        value = self.positions[self.position_index]
        if self.position_index < len(self.positions) - 1:
            self.position_index += 1
        return value

    @property
    def track(self):
        if self.position_index == 0:
            return 0
        else:
            return self.globe.bearing(self.positions[self.position_index-1],self.positions[self.position_index])

    speed = 1
