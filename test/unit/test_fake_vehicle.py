from setup_test import setup_test
setup_test()
from mock import Mock

from simulate.fake_vehicle import FakeVehicle, INITIAL_SPEED_IN_MS, TURN_FACTOR, MIN_TURN_RADIUS
from simulate.fake_vehicle_gps import FakeVehicleGPS
from globe import Globe
from position import Position
from test_utils import percentage_diff

import unittest
from math import sqrt,radians,cos,degrees

class TestFakeVehicle(unittest.TestCase):

    def setUp(self):
        self.start_position = Position(53,-2)
        self.globe = Globe()
        self.reliable_gps = FakeVehicleGPS(self.start_position,0,0.5,True)
        self.mock_logger = Mock()

    def test_should_set_the_gps_speed_immediately(self):
        vehicle = FakeVehicle(self.reliable_gps,self.globe,self.mock_logger)

        self.assertEqual(vehicle.speed,vehicle.gps.speed)

    def test_should_calculate_new_position_and_track_going_straight_ahead(self):
        bearing,time_s = 30,2
        starting_position = Position(53,-2)
        gps = FakeVehicleGPS(starting_position,bearing,INITIAL_SPEED_IN_MS,True)
        vehicle = FakeVehicle(gps,self.globe,self.mock_logger)
        expected_position = self.globe.new_position(starting_position,bearing,INITIAL_SPEED_IN_MS * time_s)

        vehicle.rudder.set_position(0)
        vehicle.timer.wait_for(time_s)
        new_position = vehicle.gps.position

        self.assertEqual(new_position.latitude, expected_position.latitude)
        self.assertEqual(new_position.longitude, expected_position.longitude)
        self.assertEqual(bearing, vehicle.gps.track)

    def test_should_turn_a_corner_if_the_rudder_is_deflected(self):
        bearing,time_s = 30,2
        starting_position = Position(53,-2)
        rudder_deflection = 10
        gps = FakeVehicleGPS(starting_position,bearing,INITIAL_SPEED_IN_MS,True)
        vehicle = FakeVehicle(gps,self.globe,self.mock_logger)
        turn_radius = vehicle._turn_radius(rudder_deflection)
        bearing_change = - vehicle._track_delta(INITIAL_SPEED_IN_MS*time_s,turn_radius)
        expected_track = bearing + bearing_change
        expected_position = self.globe.new_position(starting_position,bearing + (0.5 * bearing_change),vehicle._straightline_distance(turn_radius,bearing_change))

        vehicle.rudder.set_position(rudder_deflection)
        vehicle.timer.wait_for(time_s)
        new_position = vehicle.gps.position

        self.assertEqual(new_position.longitude, expected_position.longitude)
        self.assertEqual(new_position.latitude, expected_position.latitude)
        self.assertEqual(vehicle.gps.track, expected_track)

    def test_should_turn_right_if_rudder_deflection_is_negative(self):
        bearing,time_s = 30,2
        starting_position = Position(53,-2)
        rudder_deflection = -10
        gps = FakeVehicleGPS(starting_position,bearing,INITIAL_SPEED_IN_MS,True)
        vehicle = FakeVehicle(gps,self.globe,self.mock_logger)

        vehicle.rudder.set_position(rudder_deflection)
        vehicle.timer.wait_for(time_s)

        self.assertGreater(vehicle.gps.track,bearing)

    def test_straightline_angle_is_half_turn_angle(self):
        vehicle = FakeVehicle(self.reliable_gps,self.globe,self.mock_logger)

        self.assertEqual(vehicle._straightline_angle(47),23.5)

    def test_straightline_distance_using_radius_and_turn_angle(self):
        vehicle = FakeVehicle(self.reliable_gps,self.globe,self.mock_logger)

        self.assertLess(percentage_diff(vehicle._straightline_distance(1,90),sqrt(2)),0.0001)
        self.assertLess(percentage_diff(vehicle._straightline_distance(1,180),2),0.0001)
        self.assertLess(percentage_diff(vehicle._straightline_distance(1,-180),2),0.0001)
        self.assertLess(percentage_diff(vehicle._straightline_distance(1,60),1),0.0001)

    def test_turn_radius_always_positive_and_inversely_proportional_to_rudder_angle(self):
        vehicle = FakeVehicle(self.reliable_gps,self.globe,self.mock_logger)

        self.assertEqual(vehicle._turn_radius(30),1 + MIN_TURN_RADIUS)
        self.assertEqual(vehicle._turn_radius(-30),1 + MIN_TURN_RADIUS)
        self.assertEqual(vehicle._turn_radius(-15),2 + MIN_TURN_RADIUS)
        self.assertEqual(vehicle._turn_radius(-10),3 + MIN_TURN_RADIUS)
        self.assertEqual(vehicle._turn_radius(3),10 + MIN_TURN_RADIUS)

    def test_track_delta_based_on_distance_and_radius(self):
        vehicle = FakeVehicle(self.reliable_gps,self.globe,self.mock_logger)

        # arc of length 1 radius subtends 1 radian
        self.assertEqual(vehicle._track_delta(2,2),degrees(1))
        self.assertEqual(vehicle._track_delta(1,2),degrees(0.5))
        self.assertEqual(vehicle._track_delta(3,2),degrees(1.5))
