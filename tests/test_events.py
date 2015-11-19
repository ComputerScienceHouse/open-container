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

        ride.add_event(conn, event_time, event_time + timedelta(hours=2),
                        "My Test Event", "description",  "George")

        os.remove(DB_NAME)
        pass

    def test_list_event(self):
        DB_NAME = "list_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)

        ride.add_event(conn, event_time, event_time + timedelta(hours=2),
                        "My Test Event", "description",  "George")

        ride.list_events(conn)

        os.remove(DB_NAME)
        pass

    def test_remove_event(self):
        DB_NAME = "create_event.test"

        conn = ride.load_database(DB_NAME)

        event_time = datetime.now() + timedelta(days=1)



        wild_party = ride.add_event(conn, event_time, event_time + timedelta(hours=2),
                        "My Test Event", "description",  "George")

        ride.remove_event(conn, wild_party)

        os.remove(DB_NAME)
        pass
