from setup_test import setup_test
setup_test()

import unittest
import math

London = (51.5073509,-0.12775823)
Manchester = (53.479324,-2.2484851)
Chorlton = (53.4407973,-2.272291)
NewYork = (40.7127837, -74.0059413)
Moscow = (55.755826, 37.6173)
Sydney = (-33.8674869, 151.2069902)
Capetown = (-33.9248685, 18.4240553)
Santiago = (-33.4691199,-70.641997)

#haversine, see http://www.movable-type.co.uk/scripts/latlong.html
def distance_between(start,finish):
    start_latitude=math.radians(start[0])
    end_latitude=math.radians(finish[0])
    diff_lat = math.radians(finish[0] - start[0])  
    diff_long = math.radians(finish[1] - start[1])  
    square_half_chord_length = math.sin(diff_lat/2)**2 + math.cos(start_latitude) * math.cos(end_latitude) * math.sin(diff_long/2)**2  
    angular_distance = 2 * math.asin(math.sqrt(square_half_chord_length))  
    return 6371 * angular_distance

def percentage_diff(original,to_compare):
    return abs(to_compare-original)*100/original    

class TestDistanceCalculator(unittest.TestCase):
    def test_should_calculate_distance_to_within_one_tenth_percent(self):
        self.assertLess(percentage_diff(4.565,distance_between(Manchester,Chorlton)),0.1)
        self.assertLess(percentage_diff(262.1,distance_between(Manchester,London)),0.1)
        self.assertLess(percentage_diff(5570,distance_between(London,NewYork)),0.1)
        self.assertLess(percentage_diff(2543,distance_between(Manchester,Moscow)),0.1)
        self.assertLess(percentage_diff(11010,distance_between(Sydney,Capetown)),0.1)
        self.assertLess(percentage_diff(12560,distance_between(Capetown,NewYork)),0.1)
        self.assertLess(percentage_diff(11680,distance_between(Santiago,Chorlton)),0.1)

        print(distance_between(Santiago,Chorlton))

    def test_should_calculate_percentage_difference(self):
        self.assertEqual(percentage_diff(10,9),10)
        self.assertEqual(percentage_diff(20,21),5)
        self.assertEqual(percentage_diff(100,83),17)