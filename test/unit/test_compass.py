from setup_test import setup_test
setup_test()
import unittest
from mock import Mock
from compass import Compass

class TestCompass(unittest.TestCase):

    def  setUp(self):
        self.i2c_compass  = Mock()
        self.i2c_accel = Mock()
        self.compass = Compass(self.i2c_compass,self.i2c_accel)

    def test_returns_a_simple_north_bearing(self):
        self.mock_accel(0,0,100)
        self.mock_compass(100,0,0)
        self.assertEqual(self.compass.bearing,0)

    def test_returns_a_simple_east_bearing(self):
        self.mock_accel(0,0,100)
        self.mock_compass(0,100,0)
        self.assertEqual(self.compass.bearing,90)

    def test_returns_correct_bearings_based_on_real_data(self):
        self.mock_accel(-152,25,963)
        self.mock_compass(-71,-27,-543)
        self.assertEqual(self.compass.bearing,185)

        self.mock_accel(-187,78,1107)
        self.mock_compass(87,254,-503)
        self.assertEqual(self.compass.bearing,89)

        self.mock_accel(-8,-466,668)
        self.mock_compass(-4,520,-290)
        self.assertEqual(self.compass.bearing,92.0)

        self.mock_accel(-93,-94,1013)
        self.mock_compass(353,52,-501)
        self.assertEqual(self.compass.bearing,1.0)

        self.mock_accel(-247,-89,920)
        self.mock_compass(422,39,-465)
        self.assertEqual(self.compass.bearing,359.0)

    def mock_accel(self,x,y,z):
        self.i2c_accel.read12_2s_comp.side_effect = [x,y,z]

    def mock_compass(self,x,y,z):
        self.i2c_compass.read16_2s_comp.side_effect = [x,y,z]
