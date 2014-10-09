from gps import *
import threading
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
      if (self.gpsd.fix != None):
        self.hasfix = True
        self.heading = self.gpsd.fix.track
        self.speed = self.gpsd.fix.speed
        self.position = Position(self.gpsd.fix.latitude,self.gpsd.fix.longitude)
        self.time = self.gpsd.fix.time
      else:
        self._reset()

  def _reset(self):
    self.hasfix = False
    self.position = None
    self.heading = None
    self.speed = None
    self.time = None
    