class GpioWriter():

    def __init__(self,channel,os):
        self.channel = channel
        self.init = False
        self.os = os

    def high(self):
        self._cmd("write",1)

    def low(self):
        self._cmd("write",0)

    def _cmd(self,command,arg=""):
        if not self.init:
            self.init = True
            self._exec_cmd("mode","out")
        self._exec_cmd(command,arg)

    def _exec_cmd(self,command,arg):
        self.os.system("gpio -g {0} {1} {2}".format(command,self.channel,arg))
