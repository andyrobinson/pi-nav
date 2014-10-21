from setup_test import setup_test
setup_test()

import unittest
from position import Position
from globe import Globe

London = Position(51.5073509,-0.12775823)
Manchester = Position(53.479324,-2.2484851)
Chorlton = Position(53.4407973,-2.272291)
NewYork = Position(40.7127837, -74.0059413)
Moscow = Position(55.755826, 37.6173)
Sydney = Position(-33.8674869, 151.2069902)
Capetown = Position(-33.9248685, 18.4240553)
Santiago = Position(-33.4691199,-70.641997)

def percentage_diff(original,to_compare):
    return abs(to_compare-original)*100/abs(original)    

class TestGlobe(unittest.TestCase):
    def test_should_calculate_distance_to_within_one_tenth_percent(self):
        globe = Globe()
        
        self.assertLess(percentage_diff(4565,globe.distance_between(Manchester,Chorlton)),0.1)
        self.assertLess(percentage_diff(262100,globe.distance_between(Manchester,London)),0.1)
        self.assertLess(percentage_diff(5570000,globe.distance_between(London,NewYork)),0.1)
        self.assertLess(percentage_diff(2543000,globe.distance_between(Manchester,Moscow)),0.1)
        self.assertLess(percentage_diff(11010000,globe.distance_between(Sydney,Capetown)),0.1)
        self.assertLess(percentage_diff(12560000,globe.distance_between(Capetown,NewYork)),0.1)
        self.assertLess(percentage_diff(11680000,globe.distance_between(Santiago,Chorlton)),0.1)

    def test_should_calculate_percentage_difference(self):
        self.assertEqual(percentage_diff(10,9),10)
        self.assertEqual(percentage_diff(20,21),5)
        self.assertEqual(percentage_diff(100,83),17)
        
    def test_should_calculate_the_initial_compass_bearing_between_points(self):
        globe = Globe()
        self.assertLess(percentage_diff(200.1,globe.bearing(Manchester,Chorlton)),0.1)
        self.assertLess(percentage_diff(145.9,globe.bearing(Manchester,London)),0.1)
        self.assertLess(percentage_diff(288.3,globe.bearing(London,NewYork)),0.1)
        self.assertLess(percentage_diff(64.3,globe.bearing(London,Moscow)),0.1)
        self.assertLess(percentage_diff(357.3,globe.bearing(Santiago,NewYork)),0.1)
    
    def test_should_calculate_new_position_from_bearing_and_distance(self):
        globe = Globe()
        chorlton = globe.new_position(Manchester,200.1,4565)
        new_york = globe.new_position(London,288.3,5570000)
        self.assertLess(percentage_diff(chorlton.latitude, Chorlton.latitude),1)
        self.assertLess(percentage_diff(chorlton.longitude, Chorlton.longitude),1)
        self.assertLess(percentage_diff(new_york.longitude, NewYork.longitude),1)
        self.assertLess(percentage_diff(new_york.latitude, NewYork.latitude),1)
        
        