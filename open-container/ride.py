from __future__ import print_function
import os
import sqlite3
from datetime import datetime, date, timedelta, time

def create_database(file_name):
    conn = sqlite3.connect(file_name)

    # tables
    c = conn.cursor()

    c.execute('''create table eventList
(departureTime datetime, name text, description text, disabled integer)''')
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

    c.execute('''insert into eventList (departureTime, name, description,
disabled) values (?, ?, ?, 0)''', (time, name, description))

    conn.commit()

    c.close()

    return c.lastrowid

def list_events(conn, all_of_time=False):
    c = conn.cursor()

    c.execute('''select * from eventList where disabled is 0
order by departureTime''')

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

def remove_event(conn, id):
    c = conn.cursor()
    c.execute('update eventList set disabled=1 where rowid is %d' % id)

    return None

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

    return c.lastrowid

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

if __name__ == "__main__":
    main()
