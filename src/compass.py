# Default addresses for Adafruit LSM303DLHC
# compass = I2C(0x1e)
# accel = I2C(0x19)
from bearing import to_360
import math
class Compass:
    def __init__(self,i2c_compass,i2c_accel):
        self.compass = i2c_compass
        self.accel = i2c_accel
        self.initialised = False

    def _initialise(self):
        if self.initialised:
            return
        self.compass.write8(0, 0b01110000) # Set to 8 samples @ 15Hz
        self.compass.write8(1, 0b00100000) # 1.3 gain LSb / Gauss 1090 (default)
        self.compass.write8(2, 0b00000000) # Continuous sampling

        self.accel.write8(0x20,0b00110111) # Enable accelerometer, 25Hz, normal mode, all axes enabled
        self.accel.write8(0x23,0b00001000) # High res (12 bit) mode, LSB at lower address, default serial interface
        self.initialised = True

    # @property
    def bearing(self):
        self._initialise()
        x_acc = self.accel.read12_2s_comp(0x28)
        y_acc = self.accel.read12_2s_comp(0x2a)
        z_acc = self.accel.read12_2s_comp(0x2c)

        x_m = self.compass.read16_2s_comp(0x03)
        y_m = self.compass.read16_2s_comp(0x07)
        z_m = self.compass.read16_2s_comp(0x05)

        roll = math.atan2(y_acc,z_acc)
        pitch = math.atan2(-x_acc,z_acc) # reversing x accel makes it work
        sin_roll = math.sin(roll)
        cos_roll = math.cos(roll)
        cos_pitch = math.cos(pitch)
        sin_pitch = math.sin(pitch)

        x_final = x_m*cos_pitch + y_m*sin_roll*sin_pitch+z_m*cos_roll*sin_pitch
        y_final = y_m*cos_roll-z_m*sin_roll
        bearing = round(math.degrees(math.atan2(y_final,x_final)),0)

        return to_360(bearing)
