from __future__ import print_function
import os
import sqlite3
from datetime import datetime, date, timedelta, time

def create_database(file_name):
    conn = sqlite3.connect(file_name)

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

def load_database_from_file(file_name):
    db_conn = sqlite3.connect(file_name)

    return db_conn

def load_database(file_name):
    if not os.path.isfile(file_name):
        return create_database(file_name)
    else:
        return load_database_from_file(file_name)

def add_event(conn, time, name, description="An Event"):
    c = conn.cursor()

    c.execute('''insert into eventList (departureTime, name, description)
values (?, ?, ?)''', (time, name, description))

    conn.commit()

    c.close()

    return c.lastrowid

def list_events(conn, all_of_time=False):
    c = conn.cursor()

    c.execute('''select * from eventList order by departureTime''')

    for row in c:
        t = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
        # just check it against the date for now, more precision comes later
        if not all_of_time and t.date() < date.today():
            continue
        print(row)

    c.close()

def get_event(conn, id):
    c = conn.cursor()
    c.execute('''select * from eventList where rowid is %d''' % id)

    for row in c:
        c.close()
        return row

    c.close()
    return None

def event_exists(conn, id):
    return not get_event(conn, id) is None

def remove_event(conn, id):
    c = conn.cursor()
    c.execute('delete from eventList where rowid is %d' % id)

    conn.commit()

    c.execute('select rowid from rideList where eventId is %d' % id)
    for ride in c:
        remove_ride(ride[0])

    c.close()
    return None

def add_ride(conn, eventId, comments, driverName):
    if not event_exists(conn, eventId):
        raise Exception("Event DNE!")

    c = conn.cursor()
    c.execute('''insert into rideList (eventId, comments)
values (?, ?)''', (eventId, comments))
    conn.commit()

    rideId = c.lastrowid
    c.close()

    return (rideId, add_passenger(conn, rideId, driverName))

def list_rides(conn, eventId):
    if not event_exists(conn, eventId):
        raise Exception("Event DNE!")

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

def remove_ride(conn, carId):
    c = conn.cursor()
    c.execute('select rowid from passengers where carId is %d' % carId)
    for passenger in c:
        remove_passenger(conn, passenger)
    c.execute('delete from rideList where rowid is %d' % carId)

    conn.commit()

    c.close()

def add_passenger(conn, rideId, name):
    c = conn.cursor()
    c.execute('''insert into passengers (name, carId)
values (?, ?)''', (name, rideId))

    c.close()

    conn.commit()
    return c.lastrowid

def remove_passenger(conn, passengerId):
    c = conn.cursor()
    c.execute('delete from passengers where rowid is %d' % passengerId)
    conn.commit()

    c.close()
