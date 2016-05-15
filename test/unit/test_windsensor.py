from setup_test import setup_test
setup_test()
import unittest
from mock import Mock, call
from windsensor import WindSensor

class TestWindSensor(unittest.TestCase):

    def test_reads_14_bit_values_correctly(self):
        i2c  = Mock()
        i2c.read8.side_effect = [0x00,0x00,0x3F,0x3F,0x80,0x00,0xFF,0x00,0xFF,0x3F]
        windsensor = WindSensor(i2c)

        self.assertEqual(windsensor.angle,0)
        self.assertEqual(windsensor.angle,90)
        self.assertEqual(windsensor.angle,180)
        self.assertEqual(windsensor.angle,359)
        self.assertEqual(windsensor.angle,0)
