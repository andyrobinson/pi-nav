#! /usr/bin/python
# Written by Dan Mandle http://dan.mandle.me September 2012
# Now modified by Andy Robinson
# License: GPL 2.0
 
import os
from gps import *
from time import *
import time
import threading
 
gpsd = None #seting the global variable
 
os.system('clear') #clear the terminal (optional)

def print_attributes(obj):
  for p in filter(lambda(x):not x.startswith('__'),dir(obj)):
    print(str(p) + ': ' + str(getattr(x,p)))

class GpsPoller(threading.Thread):
  def __init__(self):
    threading.Thread.__init__(self)
    global gpsd #bring it in scope
    gpsd = gps(mode=WATCH_ENABLE) #starting the stream of info
    self.current_value = None
    self.running = True #setting the thread running to true
 
  def run(self):
    global gpsd
    while gpsp.running:
      gpsd.next() #this will continue to loop and grab EACH set of gpsd info to clear the buffer
 
if __name__ == '__main__':
  gpsp = GpsPoller() # create the thread
  try:
    gpsp.start() # start it up
    while True:
      #It may take a second or two to get good data
      #print gpsd.fix.latitude,', ',gpsd.fix.longitude,'  Time: ',gpsd.utc
 
      os.system('clear')
 
      print("\n GPS reading")
      print("----------------------------------------")
      print("latitude       " , gpsd.fix.latitude)
      print("longitude      " , gpsd.fix.longitude)
      print("time utc       " , gpsd.utc,' + ', gpsd.fix.time)
      print("altitude (m)   " , gpsd.fix.altitude)
      print("speed (m/s)    " , gpsd.fix.speed)
      print("climb          " , gpsd.fix.climb)
      print("track          " , gpsd.fix.track)
      print("mode           " , gpsd.fix.mode)
      print("long error     " , gpsd.fix.epx)
      print("lat error      " , gpsd.fix.epx)
      print("vertical error " , gpsd.fix.epv)
      print("timestmp error " , gpsd.fix.ept)
      print("speed error    " , gpsd.fix.eps)
      print("track err deg. " , gpsd.fix.epd)

      time.sleep(30) #set to whatever
 
  except (KeyboardInterrupt, SystemExit): #when you press ctrl+c
    print("\nKilling Thread...")
    gpsp.running = False
    gpsp.join() # wait for the thread to finish what it's doing
  print ("Done.\nExiting.")