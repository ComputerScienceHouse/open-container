import importlib
import os
import unittest

import open_container.ride as ride

from datetime import datetime, date, time, timedelta

class TestEvents(unittest.TestCase):
    def test_create_event(self):
        DB_NAME = "create_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        ride.add_event(conn, event_time, "My Test Event")

        event_time = event_time + timedelta(hours=4)

        ride.add_event(conn, event_time, "My Event", "A Test Event")

        os.remove(DB_NAME)
        pass

    def test_list_event(self):
        DB_NAME = "list_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        ride.add_event(conn, event_time, "My Test Event")

        event_time = event_time + timedelta(hours=4)

        ride.add_event(conn, event_time, "My Event", "A Test Event")

        ride.list_events(conn)

        os.remove(DB_NAME)
        pass

    def test_remove_event(self):
        DB_NAME = "create_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        ride.add_event(conn, event_time, "My Test Event")

        event_time = event_time + timedelta(hours=4)

        wild_party = ride.add_event(conn, event_time, "My Event", "A Test Event")

        ride.remove_event(conn, wild_party)

        os.remove(DB_NAME)
        pass
