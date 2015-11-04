import importlib
import os
import unittest

import open_container.ride as ride

class TestCreateDatabase(unittest.TestCase):
    def test_create_db(self):
        DB_NAME = "create_db.test"

        conn = ride.load_database(DB_NAME)

        os.remove(DB_NAME)

        pass
