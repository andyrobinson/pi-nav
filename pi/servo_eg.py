# From Martin Sant (martinsant.net)

import serial
import time

class Servo:
    def __init__(self,port,channel,min_pulse,max_pulse,arc):
        self.min_pulse = min_pulse
        self.max_pulse = max_pulse
        self.arc = arc
        self.channel = channel
        self.sc = serial.Serial(port)

    def closeServo(self):
        self.sc.close()

    def setPosition(self, angle):
        if angle > self.arc or angle < 0:
            angle=int(self.arc/2)
        pulse_range = self.max_pulse-self.min_pulse
        position = int(((float(angle)/self.arc) * pulse_range) + self.min_pulse) * 4
        poslo = (position & 0x7f)
        poshi = (position >> 7) & 0x7f
        data =  chr(0xaa) + chr(0x0c) + chr(0x04) + chr(self.channel) + chr(poslo) + chr(poshi)
        self.sc.write(data)

    def getPosition(self):
        chan  = self.channel &0x7f
        data =  chr(0xaa) + chr(0x0c) + chr(0x10) + chr(self.channel)
        self.sc.write(data)
        w1 = ord(self.sc.read())
        w2 = ord(self.sc.read())
        return w1, w2

    def getErrors(self):
        data =  chr(0xaa) + chr(0x0c) + chr(0x21)
        self.sc.write(data)
        w1 = ord(self.sc.read())
        w2 = ord(self.sc.read())
        return w1, w2


# MAIN

s = Servo('/dev/ttyACM0',0,500,2500,180)         
val = '0'

while(val <> 'q'):
    val = raw_input('enter angle (0-180), q to quit: ')
    if val != 'q':
        angle = int(val) 
    else:
        angle = 0
    s.setPosition(angle)
    time.sleep(0.1)
    print 'position', s.getPosition(), s.getErrors()


