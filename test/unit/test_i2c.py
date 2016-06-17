from setup_test import setup_test
setup_test()
import unittest
from mock import Mock

class SmbusStub():

    def read_byte_data(self,address,register):
        result = self.data[0]
        if len(self.data) > 1:
            self.data = self.data[1:]
        return result

    def setup_byte_data(self,data_array):
        self.data = data_array

import sys
stubSmbus = SmbusStub()
mockSmbusModule = Mock()
mockSmbusModule.SMBus.side_effect = lambda value: stubSmbus
sys.modules['smbus'] = mockSmbusModule
from i2c import I2C

class TestI2C(unittest.TestCase):

    def test_should_return_configured_8_bit_data(self):
        i2c = I2C(44)
        stubSmbus.setup_byte_data([0xFF])
        self.assertEqual(i2c.read8(23), 0xFF)

    def test_should_return_consecutive_data_in_one_value(self):
        i2c = I2C(44)
        stubSmbus.setup_byte_data([0x01,0x02])
        self.assertEqual(i2c.read16(23,high_low=True), 0x0102)

    def test_should_return_reverse_consecutive_data_in_one_value_with_false(self):
        i2c = I2C(44)
        stubSmbus.setup_byte_data([0x01,0x02])
        self.assertEqual(i2c.read16(23,high_low=False), 0x0201)

    def test_should_treat_bytes_as_2s_comp(self):
        i2c = I2C(44)
        stubSmbus.setup_byte_data([0x01,0x02])
        self.assertEqual(i2c.read16_2s_comp(23), 258)
        stubSmbus.setup_byte_data([0xFF,0xF9])
        self.assertEqual(i2c.read16_2s_comp(23), -7)
