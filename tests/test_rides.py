import importlib
import os
import unittest

from datetime import datetime, date, time, timedelta

class TestRides(unittest.TestCase):
    def test_create_ride(self):
        DB_NAME = "create_event.test"

        ride = importlib.import_module("open-container.ride")

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        ride.add_event(conn, event_time, "My Test Event")

        event_time = event_time + timedelta(hours=4)

        wild_party = ride.add_event(conn, event_time, "My Event", "A Test Event")

        ride.add_ride(conn, wild_party, "Party Van", 8, "Loothelion")

        os.remove(DB_NAME)
        pass

    def test_list_rides(self):
        DB_NAME = "create_event.test"

        ride = importlib.import_module("open-container.ride")

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        ride.add_event(conn, event_time, "My Test Event")

        event_time = event_time + timedelta(hours=4)

        wild_party = ride.add_event(conn, event_time, "My Event", "A Test Event")

        ride.add_ride(conn, wild_party, "Party Van", 8, "Loothelion")

        ride.list_rides(conn, wild_party)

        os.remove(DB_NAME)
        pass

    def test_remove_ride(self):
        DB_NAME = "create_event.test"

        ride = importlib.import_module("open-container.ride")

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        ride.add_event(conn, event_time, "My Test Event")

        event_time = event_time + timedelta(hours=4)

        wild_party = ride.add_event(conn, event_time, "My Event", "A Test Event")

        party_van = ride.add_ride(conn, wild_party, "Party Van", 8, "Loothelion")

        ride.list_rides(conn, wild_party)

        ride.remove_ride(conn, party_van[0])

        ride.list_rides(conn, wild_party)

        os.remove(DB_NAME)
        pass
