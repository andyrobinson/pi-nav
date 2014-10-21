from math import sin,asin,cos,atan2,radians,degrees,sqrt

EARTH_RADIUS_METRES = 6371000

# haversine & bearing, see http://www.movable-type.co.uk/scripts/latlong.html
class Globe():

    def distance_between(self,start,finish):
        start_lat, end_lat, diff_lat, diff_long =self._to_radians(start.latitude,finish.latitude,finish.latitude-start.latitude,finish.longitude-start.longitude)
        square_half_chord_length = sin(diff_lat/2)**2 + cos(start_lat) * cos(end_lat) * sin(diff_long/2)**2  
        angular_distance = 2 * asin(sqrt(square_half_chord_length))
        return EARTH_RADIUS_METRES * angular_distance

    def bearing(self,start,finish):
        start_lat,end_lat,diff_long=self._to_radians(start.latitude,finish.latitude,finish.longitude-start.longitude)
        y = sin(diff_long) * cos(end_lat)
        x = cos(start_lat) * sin(end_lat) - (sin(start_lat) * cos(end_lat) * cos(diff_long))
        return (360 + degrees(atan2(y,x))) % 360
        
    def _to_radians(self,*degs):
        return map((lambda x: radians(x)), degs)