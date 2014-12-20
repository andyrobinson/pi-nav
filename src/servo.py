# Pololu Maestro USB servo controller
# see http://www.pololu.com/docs/0J40
COMMAND_BASE = chr(0xaa) + chr(0x0c)
SET_POSITION_COMMAND = COMMAND_BASE + chr(0x04)
GET_POSITION_COMMAND = COMMAND_BASE + chr(0x10)
GET_ERRORS_COMMAND = COMMAND_BASE + chr(0x21)

class Servo():
    def __init__(self,serial,channel,min_pulse,min_angle,max_pulse,max_angle):
        self.serial = serial
        self.channel = channel
        self.min_pulse = min_pulse
        self.min_angle = min_angle
        self.total_arc = max_angle - min_angle
        self.pulse_range = max_pulse-min_pulse

    def last7bits(self,value):
        return chr(value & 0x7f)

    def bits8to14(self,value):
        return self.last7bits(value >> 7)

    def set_position(self,angle):
        zeroed_angle = angle - self.min_angle
        position_pulse = int(((float(zeroed_angle)/self.total_arc) * self.pulse_range) + self.min_pulse) * 4
        position_low = self.last7bits(position_pulse)
        position_high = self.bits8to14(position_pulse)
        self.serial.write(SET_POSITION_COMMAND + chr(self.channel) + position_high + position_low)

    def get_position(self):
        data =  GET_POSITION_COMMAND + chr(self.channel)
        self.serial.write(data)
        position_low = ord(self.serial.read())
        position_high = ord(self.serial.read())
        print 'position high, low: ' + str(position_high) + ',' + str(position_low)
        agg_position = (position_high << 7) + position_low
        print 'aggregate position: ' + str(agg_position)
        print 'corrected by 4 and for min_pulse: ' + str((agg_position/4) - self.min_pulse) 
        position = (float(((position_high << 7) + position_low)/4 - self.min_pulse)/self.pulse_range) * self.total_arc + self.min_angle
        print 'final position: ' + str(position)
        return position

    def get_errors(self):
        self.serial.write(GET_ERRORS_COMMAND)
        error1 = ord(self.serial.read())
        error2 = ord(self.serial.read())
        return error1,error2    