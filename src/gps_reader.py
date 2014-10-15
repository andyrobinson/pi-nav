# Based on implementation written by Dan Mandle http://dan.mandle.me September 2012
# License: GPL 2.0
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
        self.track = self.gpsd.fix.track
        self.speed = self.gpsd.fix.speed
        self.position = Position(self.gpsd.fix.latitude,self.gpsd.fix.longitude,self.gpsd.fix.epy,self.gpsd.fix.epx)
        self.time = self.gpsd.fix.time
        self.speed_error = self.gpsd.fix.eps
        self.track_error = self.gpsd.fix.epd

  def _reset(self):
    self.hasfix = False
    self.position = Position(NaN,NaN)
    self.track = NaN
    self.speed = NaN
    self.time = NaN
    self.speed_error = NaN
    self.track_error = NaN
    