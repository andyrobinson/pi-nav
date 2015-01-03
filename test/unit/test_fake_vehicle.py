from setup_test import setup_test
setup_test()
from mock import Mock

from simulate.fake_vehicle import FakeVehicle, INITIAL_SPEED_IN_MS, TURN_FACTOR, MIN_TURN_RADIUS
from simulate.fake_vehicle_gps import FakeVehicleGPS
from globe import Globe
from position import Position

import unittest
from math import sqrt,radians,cos

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

    def test_should_calculate_new_position_and_track_going_straight_ahead(self):
        bearing,time_s = 30,2
        starting_position = Position(53,-2)
        gps = FakeVehicleGPS(starting_position,bearing,INITIAL_SPEED_IN_MS,True)
        vehicle = FakeVehicle(gps,self.globe,self.mock_logger)
        vehicle.rudder.set_position(0)
        vehicle.timer.wait_for(time_s)

        expected_position = self.globe.new_position(starting_position,bearing,INITIAL_SPEED_IN_MS * time_s)
        new_position = vehicle.gps.position

        self.assertEqual(new_position.latitude, expected_position.latitude)
        self.assertEqual(new_position.longitude, expected_position.longitude)
        self.assertEqual(bearing, vehicle.gps.track)

    def test_should_turn_a_corner_if_the_rudder_is_deflected(self):
        bearing,time_s = 30,2
        starting_position = Position(53,-2)
        gps = FakeVehicleGPS(starting_position,bearing,INITIAL_SPEED_IN_MS,True)
        vehicle = FakeVehicle(gps,self.globe,self.mock_logger)

        vehicle.rudder.set_position(10)
        vehicle.timer.wait_for(time_s)

        expected_position = self.globe.new_position(starting_position,bearing,INITIAL_SPEED_IN_MS * time_s)
        new_position = vehicle.gps.position

        self.assertEqual(new_position.latitude, expected_position.latitude)
        self.assertEqual(new_position.longitude, expected_position.longitude)
        self.assertEqual(bearing, vehicle.gps.track)

    def straightline_distance_for_given_turn_and_radius(radius,angle_in_deg):
        return radius * sqrt(2 - 2 * cos(radians(angle_in_deg)))

    def straightline_angle_for_given_turn_angle(angle_in_deg):
        return float(angle_in_deg) / 2

    def turn_angle_given_speed_time_and_rudder_angle(speed,time,rudder_angle):
        if rudder_angle == 0:
            return 100000
        distance = float(speed) * time
        turn_radius = (TURN_FACTOR/rudder_angle) + MIN_TURN_RADIUS
        return distance/turn_radius 

