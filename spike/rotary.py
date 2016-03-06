#!/usr/bin/python
#
# Basic reading of AS5048B I2c rotary position sensor
# For some reason the high and low bytes appear to be reversed
#
import smbus
import time
import math

bus = smbus.SMBus(1)
address = 0x40
MAX_RAW = 0x3FFF

def read_raw_angle(adr):
    high = bus.read_byte_data(address, 0xFF)
    low = bus.read_byte_data(address, 0xFE)
    val = (high << 6) + (low & 0x3F)
    return val

while True:
    try:
        raw_angle = read_raw_angle(0xfe)
        degrees = 360 * (raw_angle/float(MAX_RAW))
        print "raw, angle",raw_angle,degrees
        time.sleep(1)
    except(KeyboardInterrupt):
        quit()


