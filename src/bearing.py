def angle_between(bearing1,bearing2):
    diff = bearing2 - bearing1
    if diff <= -180:
        diff = diff + 360
    if diff > 180:
        diff = diff - 360
    return diff

def to_360(bearing):
    if bearing < 0:
        return bearing + 360
    return bearing