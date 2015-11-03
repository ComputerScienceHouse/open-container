import importlib
import os
import unittest

class TestCreateDatabase(unittest.TestCase):
    def test_create_db(self):
        DB_NAME = "create_db.test"

        ride = importlib.import_module("open-container.ride")

        conn = ride.load_database(DB_NAME)

        os.remove(DB_NAME)

        pass
