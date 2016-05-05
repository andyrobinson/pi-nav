import smbus

class I2C:
    def __init__(self,address):
        self.address = address
        self.bus = smbus.SMBus(1)

    def read8(self,register):
        return self.bus.read_byte_data(self.address, register)

    def read16(self, register, high_low):
        first = self.bus.read_byte_data(self.address, register)
        second = self.bus.read_byte_data(self.address, register+1)
        if high_low:
           val = (first << 8) + second
        else:
           val = (second << 8) + first
        return val

    def read16_2s_comp(self,register,high_low=True):
        val = self.read16(register,high_low)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def read12_2s_comp(self,register):
        return self.read16_2s_comp(register,False) >> 4

    def write8(self,register, value):
        self.bus.write_byte_data(self.address, register, value)
