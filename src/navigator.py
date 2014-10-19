

class Navigator():
    def __init__(self,point_navigator):
        self.point_navigator = point_navigator
        
    def follow_route(self,waypoints):
        self.point_navigator.to(waypoints[0], self.follow_route , waypoints[1:])