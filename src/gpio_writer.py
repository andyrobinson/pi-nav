import os
import time

class GpioWriter():

    def __init__(self,channel):
        self.channel = channel
        self._cmd("mode","out")

    def high(self):
        self._cmd("write",1)

    def low(self):
        self._cmd("write",0)

    def _cmd(self,command,arg=""):
        os.system("gpio -g {0} {1} {2}.format(command,self.channel,arg))
