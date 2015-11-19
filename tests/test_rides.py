import importlib
import os
import unittest

import open_container.ride as ride

from datetime import datetime, date, time, timedelta

class TestRides(unittest.TestCase):
    def test_create_ride(self):
        DB_NAME = "create_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        wild_party = ride.add_event(conn, event_time, event_time + timedelta(hours=2),
                        "My Test Event", "description",  "George")

        party_van = ride.add_ride(conn, wild_party,
                "Party Van", 8, "Loothelion",
                event_time - timedelta(minutes=30),
                event_time + timedelta(hours=1))

        os.remove(DB_NAME)
        pass

    def test_list_rides(self):
        DB_NAME = "create_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        wild_party = ride.add_event(conn, event_time, event_time + timedelta(hours=2),
                        "My Test Event", "description",  "George")

        party_van = ride.add_ride(conn, wild_party,
                "Party Van", 8, "Loothelion",
                event_time - timedelta(minutes=30),
                event_time + timedelta(hours=1))

        ride.list_rides(conn, wild_party)

        os.remove(DB_NAME)
        pass

    def test_remove_ride(self):
        DB_NAME = "create_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        wild_party = ride.add_event(conn, event_time, event_time + timedelta(hours=2),
                        "My Test Event", "description",  "George")

        party_van = ride.add_ride(conn, wild_party,
                "Party Van", 8, "Loothelion",
                event_time - timedelta(minutes=30),
                event_time + timedelta(hours=1))

        ride.list_rides(conn, wild_party)

        ride.remove_ride(conn, party_van)

        ride.list_rides(conn, wild_party)

        os.remove(DB_NAME)
        pass
