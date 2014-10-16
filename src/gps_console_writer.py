import os

class GpsConsoleWriter():
    def __init__(self,gps_reader):
        self.gps_reader = gps_reader

    def write(self):
        os.system('clear')

        print("\n GPS reading")
        print("-------------------------------------------")
        print("latitude       " , self.gps_reader.position.latitude)
        print("longitude      " , self.gps_reader.position.longitude)
        print("long error     " , self.gps_reader.position.long_error)
        print("lat error      " , self.gps_reader.position.lat_error)
        print("time           " , self.gps_reader.time)
        print("speed (m/s)    " , self.gps_reader.speed)
        print("track          " , self.gps_reader.track)
        print("speed error    " , self.gps_reader.speed_error)
        print("track err deg. " , self.gps_reader.track_error)
        print("-------------------------------------------")
        return True
        