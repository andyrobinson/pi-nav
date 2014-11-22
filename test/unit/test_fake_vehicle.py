from setup_test import setup_test
setup_test()
from mock import Mock

from simulate.fake_vehicle import FakeVehicle
from simulate.fake_vehicle_gps import FakeVehicleGPS
from globe import Globe
from position import Position

import unittest

class TestFakeVehicle(unittest.TestCase):

    def setUp(self):
        self.start_position = Position(53,-2)
        self.globe = Globe()
        self.reliable_gps = FakeVehicleGPS(self.start_position,0,0.5,True)
        self.mock_logger = Mock()

    def test_should_have_covered_distance_calculated_by_time_x_speed(self):
        vehicle = FakeVehicle(self.reliable_gps,self.globe,self.mock_logger)
        bearing = 90
        time_to_steer = 60

        vehicle.steer_course(bearing,time_to_steer)
        end_position = vehicle.gps.position

        distance_covered = self.globe.distance_between(self.start_position,end_position)

        self.assertEqual(round(distance_covered,1),round(time_to_steer * vehicle.speed,1))

    def test_should_set_the_gps_speed_immediately(self):
        vehicle = FakeVehicle(self.reliable_gps,self.globe,self.mock_logger)

        self.assertEqual(vehicle.speed,vehicle.gps.speed)

