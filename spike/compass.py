#!/usr/bin/python
#
# courtesy of http://blog.bitify.co.uk/2013/11/connecting-and-calibrating-hmc5883l.html
#
import smbus
import time
import math

class I2C:
    def __init__(self,address):
        self.address = address
        self.bus = smbus.SMBus(1)

    def read8(self,register):
        return self.bus.read_byte_data(self.address, register)

    def read16(self, register):
        high = self.bus.read_byte_data(self.address, register)
        low = self.bus.read_byte_data(self.address, register+1)
        val = (high << 8) + low
        return val

    def read16_2s_comp(self,register):
        val = self.read16(register)
        if (val >= 0x8000):
            return -((65535 - val) + 1)
        else:
            return val

    def write8(self,register, value):
        self.bus.write_byte_data(self.address, register, value)

compass = I2C(0x1e)
compass.write8(0, 0b01110000) # Set to 8 samples @ 15Hz
compass.write8(1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
compass.write8(2, 0b00000000) # Continuous sampling

def print_compass():
    x_out = compass.read16_2s_comp(3) 
    y_out = compass.read16_2s_comp(7) 
    z_out = compass.read16_2s_comp(5)
    #y_adj = y_out*0.95 + 13
    y_adj = y_out
    #x_adj = x_out - 23
    x_adj = x_out
    bearing  = math.atan2(y_adj, x_adj) 
    if (bearing < 0):
        bearing += 2 * math.pi
    print x_adj,y_adj,z_out, " bearing: ", round(math.degrees(bearing),0)
    #print x_adj,",",y_adj,",",z_out
    #print x_out,",",y_out,",",z_out

while True:
    try:
        print_compass()
        time.sleep(0.1)
    except(KeyboardInterrupt):
        quit()

