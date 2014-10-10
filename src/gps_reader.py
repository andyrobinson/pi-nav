from gps import *
import threading
import math
from position import Position
                
class GpsReader(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    self.gpsd = gps(mode=WATCH_ENABLE)
    self.running = True
    self._reset()
 
  def run(self):
    while self.running:
      self.gpsd.next()
      if math.isnan(self.gpsd.fix.latitude):
        self._reset()
      else:
        self.hasfix = True
        self.heading = self.gpsd.fix.track
        self.speed = self.gpsd.fix.speed
        self.position = Position(self.gpsd.fix.latitude,self.gpsd.fix.longitude)
        self.time = self.gpsd.fix.time

  def _reset(self):
    self.hasfix = False
    self.position = None
    self.heading = None
    self.speed = None
    self.time = None
    