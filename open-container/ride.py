from __future__ import print_function
import os
import sqlite3
from datetime import datetime, date, timedelta, time

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

def list_events(conn, all_of_time=False):
    c = conn.cursor()

    c.execute('select * from eventList order by departureTime')

    for row in c:
        t = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
        # just check it against the date for now, more precision comes later
        if not all_of_time and t.date() < date.today():
            continue
        print(row)

    c.close()

def get_event(conn, id):
    c = conn.cursor()
    c.execute('select * from eventList where rowid is %d' % id)

    for row in c:
        c.close()
        return row

    c.close()
    return None

def event_exists(conn, id):
    return not get_event(conn, id) is None

def add_ride(conn, eventId, comments, driverName):
    if not event_exists(conn, eventId):
        return None

    c = conn.cursor()
    c.execute('''insert into rideList (eventId, comments)
values (?, ?)''', (eventId, comments))
    print("last row %d" % c.lastrowid)
    c.execute('''insert into passengers (name, carId)
values (?, ?)''', (driverName, c.lastrowid))
    conn.commit()
    c.close()

def list_rides(conn, eventId):
    c = conn.cursor()
    c.execute('select rowid, comments from rideList where eventId is %d' % eventId)

    for ride in c:
        print("ride: ")
        print(ride)
        d = conn.cursor()
        d.execute('select * from passengers where carId is %d' % ride[0])
        print("passengers: ")
        for passenger in d:
            print("\t", passenger)
        d.close()
    c.close()

def main():
    db_conn = None

    if not os.path.isfile(DB_NAME):
        db_conn = create_database()
    else:
        db_conn = sqlite3.connect(DB_NAME)

    # add party NOW!
    add_event(db_conn, datetime.now(), "Test Event")

    print("events: ")
    list_events(db_conn)

    add_ride(db_conn, 2, "blash", "liam")

    print(event_exists(db_conn, 2))

    print("rides: ")
    list_rides(db_conn, 2)
    pass

if __name__ == "__main__":
    main()
