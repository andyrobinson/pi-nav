def angle_between(bearing1,bearing2):
    diff = bearing2 - bearing1
    if diff <= -180:
        diff = diff + 360
    if diff > 180:
        diff = diff - 360
    return diff

def to_360(bearing):
    return (bearing + 360) % 360

def moving_avg(avg,next_sample,smoothing):
    diff = angle_between(avg,next_sample)
    return to_360(avg + (diff/smoothing))
