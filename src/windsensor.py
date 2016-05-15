MAX_RAW_14_BITS = 0x3FFF

class WindSensor:

    def __init__(self,i2c):
        self.i2c = i2c

    @property
    def angle(self):
        high8bits = self.i2c.read8(0xFF)
        low6bits = self.i2c.read8(0xFE)
        raw_value_14_bits = self._shift_left_6_bits(high8bits) + self._lowest_6_bits(low6bits)
        degrees = round(360 * (raw_value_14_bits/float(MAX_RAW_14_BITS)),0) % 360
        return degrees

    def _lowest_6_bits(self,byte):
        return byte & 0x3F

    def _shift_left_6_bits(self,word):
        return word << 6
