class FakeMovingGPS():
    def __init__(self,positions):
        self.positions = positions
        
    def get_position(self):
        value = self.positions[0]
        if len(self.positions) > 1:
            self.positions = self.positions[1:]
        return value
        
    position = property(get_position)    
        
