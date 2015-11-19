import importlib
import os
import unittest

import open_container.ride as ride

from datetime import datetime, date, time, timedelta

class TestPassengers(unittest.TestCase):
    def test_add_passenger(self):
        DB_NAME = "create_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        wild_party = ride.add_event(conn, event_time, event_time + timedelta(hours=2),
                        "My Test Event", "description",  "George")

        party_van = ride.add_ride(conn, wild_party,
                "Party Van", 8, "Loothelion",
                event_time - timedelta(minutes=30),
                event_time + timedelta(hours=1))

        ride.add_passenger(conn, party_van, "Isaac")

        ride.add_passenger(conn, party_van, "Nate")

        ride.add_passenger(conn, party_van, "Matt")

        os.remove(DB_NAME)
        pass

    def test_list_passengers(self):
        DB_NAME = "create_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        wild_party = ride.add_event(conn, event_time, event_time + timedelta(hours=2),
                        "My Test Event", "description",  "George")

        party_van = ride.add_ride(conn, wild_party,
                "Party Van", 8, "Loothelion",
                event_time - timedelta(minutes=30),
                event_time + timedelta(hours=1))

        ride.add_passenger(conn, party_van, "Isaac")

        ride.add_passenger(conn, party_van, "Nate")

        ride.add_passenger(conn, party_van, "Matt")

        ride.list_rides(conn, wild_party)

        os.remove(DB_NAME)
        pass

    def test_remove_passenger(self):
        DB_NAME = "create_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        wild_party = ride.add_event(conn, event_time, event_time + timedelta(hours=2),
                        "My Test Event", "description",  "George")

        party_van = ride.add_ride(conn, wild_party,
                "Party Van", 8, "Loothelion",
                event_time - timedelta(minutes=30),
                event_time + timedelta(hours=1))

        isaac = ride.add_passenger(conn, party_van, "Isaac")

        ride.add_passenger(conn, party_van, "Nate")

        ride.add_passenger(conn, party_van, "Matt")

        ride.list_rides(conn, wild_party)

        ride.remove_passenger(conn, isaac)

        ride.list_rides(conn, wild_party)

        os.remove(DB_NAME)
        pass

    def test_too_many_passengers(self):
        DB_NAME = "create_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        wild_party = ride.add_event(conn, event_time, event_time + timedelta(hours=2),
                        "My Test Event", "description",  "George")

        party_van = ride.add_ride(conn, wild_party,
                "Party Van", 8, "Loothelion",
                event_time - timedelta(minutes=30),
                event_time + timedelta(hours=1))

        isaac = ride.add_passenger(conn, party_van, "Isaac")

        ride.add_passenger(conn, party_van, "Nate")

        ride.add_passenger(conn, party_van, "Matt")

        ride.add_passenger(conn, party_van, "Andrew")

        ride.add_passenger(conn, party_van, "Julien")

        ride.add_passenger(conn, party_van, "Rose")

        ride.add_passenger(conn, party_van, "Max")

        try:
            ride.add_passenger(conn, party_van, "Brandon/Tanat")
        except Exception:
            print("This should be reached, don't worry about it!")

        ride.list_rides(conn, wild_party)

        ride.remove_passenger(conn, isaac)

        ride.list_rides(conn, wild_party)

        os.remove(DB_NAME)
        pass
