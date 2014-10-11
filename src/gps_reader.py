try:
    from gps import *
except ImportError, e:
    if e.message != 'No module named gps':
        raise

import threading
from position import Position
                
NaN = float('nan')

class GpsReader(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.gpsd = gps(mode=WATCH_ENABLE)
    self.running = True
    self._reset()
 
  def run(self):
    while self.running:
      self.gpsd.next()
      if (not(hasattr(self.gpsd.fix,'mode')) or self.gpsd.fix.mode == MODE_NO_FIX):
        self._reset()
      else:
        self.hasfix = True
        self.heading = self.gpsd.fix.track
        self.speed = self.gpsd.fix.speed
        self.position = Position(self.gpsd.fix.latitude,self.gpsd.fix.longitude)
        self.time = self.gpsd.fix.time

  def _reset(self):
    self.hasfix = False
    self.position = Position(NaN,NaN)
    self.heading = NaN
    self.speed = NaN
    self.time = NaN
    