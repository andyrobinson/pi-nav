#!/usr/bin/python
#
# courtesy of http://blog.bitify.co.uk/2013/11/connecting-and-calibrating-hmc5883l.html
#
import smbus
import time
import math

bus = smbus.SMBus(1)
address = 0x1e


def read_byte(adr):
    return bus.read_byte_data(address, adr)

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def write_byte(adr, value):
    bus.write_byte_data(address, adr, value)

write_byte(0, 0b01110000) # Set to 8 samples @ 15Hz
write_byte(1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
write_byte(2, 0b00000000) # Continuous sampling

while True:
    try:     
        x_out = read_word_2c(3) * 1.01
        y_out = read_word_2c(7) * 0.9
        z_out = read_word_2c(5)
        y_adj = y_out * 1.1 + 335
        x_adj = x_out - 215
        bearing  = math.atan2(y_adj, x_adj) 
        if (bearing < 0):
            bearing += 2 * math.pi
        print x_adj,y_adj,z_out, " bearing: ", math.degrees(bearing)
        #print x_adj,",",y_adj
        time.sleep(0.1)
    except(KeyboardInterrupt):
        quit()
