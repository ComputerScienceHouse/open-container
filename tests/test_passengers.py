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

        ride.add_event(conn, event_time, "My Test Event")

        event_time = event_time + timedelta(hours=4)

        wild_party = ride.add_event(conn, event_time, "My Event", "A Test Event")

        party_van = ride.add_ride(conn, wild_party, "Party Van", 8, "Loothelion")

        ride.add_passenger(conn, party_van[0], "Isaac")

        ride.add_passenger(conn, party_van[0], "Nate")

        ride.add_passenger(conn, party_van[0], "Matt")

        os.remove(DB_NAME)
        pass

    def test_list_passengers(self):
        DB_NAME = "create_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        ride.add_event(conn, event_time, "My Test Event")

        event_time = event_time + timedelta(hours=4)

        wild_party = ride.add_event(conn, event_time, "My Event", "A Test Event")

        party_van = ride.add_ride(conn, wild_party, "Party Van", 8, "Loothelion")

        ride.add_passenger(conn, party_van[0], "Isaac")

        ride.add_passenger(conn, party_van[0], "Nate")

        ride.add_passenger(conn, party_van[0], "Matt")

        ride.list_rides(conn, wild_party)

        os.remove(DB_NAME)
        pass

    def test_remove_passenger(self):
        DB_NAME = "create_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        ride.add_event(conn, event_time, "My Test Event")

        event_time = event_time + timedelta(hours=4)

        wild_party = ride.add_event(conn, event_time, "My Event", "A Test Event")

        party_van = ride.add_ride(conn, wild_party, "Party Van", 8, "Loothelion")

        isaac = ride.add_passenger(conn, party_van[0], "Isaac")

        ride.add_passenger(conn, party_van[0], "Nate")

        ride.add_passenger(conn, party_van[0], "Matt")

        ride.list_rides(conn, wild_party)

        ride.remove_passenger(conn, isaac)

        ride.list_rides(conn, wild_party)

        os.remove(DB_NAME)
        pass

    def test_too_many_passengers(self):
        DB_NAME = "create_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        ride.add_event(conn, event_time, "My Test Event")

        event_time = event_time + timedelta(hours=4)

        wild_party = ride.add_event(conn, event_time, "My Event", "A Test Event")

        party_van = ride.add_ride(conn, wild_party, "Party Van", 8, "Loothelion")

        isaac = ride.add_passenger(conn, party_van[0], "Isaac")

        ride.add_passenger(conn, party_van[0], "Nate")

        ride.add_passenger(conn, party_van[0], "Matt")

        ride.add_passenger(conn, party_van[0], "Andrew")

        ride.add_passenger(conn, party_van[0], "Julien")

        ride.add_passenger(conn, party_van[0], "Rose")

        ride.add_passenger(conn, party_van[0], "Max")

        try:
            ride.add_passenger(conn, party_van[0], "Brandon/Tanat")
        except Exception:
            print("This should be reached, don't worry about it!")

        ride.list_rides(conn, wild_party)

        ride.remove_passenger(conn, isaac)

        ride.list_rides(conn, wild_party)

        os.remove(DB_NAME)
        pass
