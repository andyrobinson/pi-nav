MAX_RAW = 0x3FFF

class WindSensor:

    def __init__(self,i2c):
        self.i2c = i2c

    @property
    def angle(self):
        high = self.i2c.read8(0xFF)
        low = self.i2c.read8(0xFE)
        raw_value = (high << 6) + (low & 0x3F)
        degrees = round(360 * (raw_value/float(MAX_RAW)),0) % 360
        return degrees
