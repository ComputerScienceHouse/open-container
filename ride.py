import os
import sqlite3
from datetime import datetime, date, time

DB_NAME = "test.db"

def create_database():
    conn = sqlite3.connect(DB_NAME)

    # tables
    c = conn.cursor()

    c.execute('''create table eventList
(departureTime datetime, name text, description text)''')
    c.execute('''create table rideList
(eventId integer, comments text)''')
    c.execute('''create table passengers
(name text, carid integer)''')

    conn.commit()

    c.close()

    return conn

def add_event(conn, time, name, description="An Event"):
    c = conn.cursor()

    c.execute('''insert into eventList (departureTime, name, description)
values (?, ?, ?)''', (time, name, description))

    conn.commit()

    c.close()

def list_events(conn):
    c = conn.cursor()

    c.execute('select * from eventList order by departureTime')

    for row in c:
        print(row)

def main():
    db_conn = None

    if not os.path.isfile(DB_NAME):
        db_conn = create_database()
    else:
        db_conn = sqlite3.connect(DB_NAME)

    add_event(db_conn, datetime.now(), "Test Event")

    list_events(db_conn)
    pass

if __name__ == "__main__":
    main()
