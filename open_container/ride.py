from __future__ import print_function
import os
import sqlite3
from datetime import datetime, date, timedelta, time
from flask import Flask, jsonify, request

app = Flask(__name__)

DB_NAME = "test.db"

@app.route('/create/event', methods=['POST'])
def http_create_event():
    db_conn = load_database(DB_NAME)

    error = None

    event_time = timestr_to_datetime(request.form['time'])

    name = request.form['name']
    description = request.form['description']

    event_id = add_event(db_conn, event_time, name, description)

    return jsonify({"id":event_id})

@app.route('/create/ride', methods=['POST'])
def http_create_ride():
    db_conn = load_database(DB_NAME)

    error = None

    event_id = int(request.form['eventId'])

    comments = request.form['comments']

    capacity = int(request.form['capacity'])

    driver_name = request.form['driverName']

    ride_data = add_ride(db_conn, event_id, comments, capacity, driver_name)

    return jsonify({"rideId": ride_data[0], "driverId": ride_data[1]})

@app.route('/create/passenger', methods=['POST'])
def http_create_passenger():
    db_conn = load_database(DB_NAME)

    error = None

    car_id = int(request.form['carId'])

    name = request.form['name']

    passenger_data = add_passenger(db_conn, car_id, name)

    return jsonify({"id": passenger_data})

@app.route('/list/events', methods=['POST'])
def http_list_events():
    db_conn = load_database(DB_NAME)

    return jsonify({"events": list_events(db_conn)})

@app.route('/list/rides', methods=['POST'])
def http_list_rides():
    db_conn = load_database(DB_NAME)

    event_id = int(request.form['id'])

    return jsonify({"rides": list_rides(db_conn, event_id)})

@app.route('/remove/event', methods=['POST'])
def http_remove_event():
    db_conn = load_database(DB_NAME)

    event_id = int(request.form['id'])

    remove_event(db_conn, event_id)

    return ""

@app.route('/remove/ride', methods=['POST'])
def http_remove_ride():
    db_conn = load_database(DB_NAME)

    ride_id = int(request.form['id'])

    remove_ride(db_conn, ride_id)

    return ""

@app.route('/remove/passenger', methods=['POST'])
def http_remove_passenger():
    db_conn = load_database(DB_NAME)

    passenger_id = int(request.form['id'])

    remove_passenger(db_conn, passenger_id)

    return ""

def timestr_to_datetime(timestr):
    return datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S.%f")

def datetime_to_timestr(date_time):
    return date_time.strftime("%Y-%m-%d %H:%M:%S.%f")

def create_database(file_name):
    conn = sqlite3.connect(file_name)

    # tables
    c = conn.cursor()

    c.execute('''create table eventList
(departureTime datetime, name text, description text)''')
    c.execute('''create table rideList
(eventId integer, capacity integer, comments text)''')
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

    c.execute('''select departureTime, name, description, rowid from eventList order by departureTime''')

    events = []

    for row in c:
        t = datetime.strptime(row[0], "%Y-%m-%d %H:%M:%S.%f")
        # just check it against the date for now, more precision comes later
        if not all_of_time and t.date() < date.today():
            continue
        print(row)
        events.append({"id": row[3], "time": row[0], "name": row[1], "description": row[2]})

    c.close()

    return events

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

def add_ride(conn, eventId, comments, capacity, driverName):
    if not event_exists(conn, eventId):
        raise Exception("Event DNE!")

    c = conn.cursor()
    c.execute('''insert into rideList (eventId, capacity, comments)
values (?, ?, ?)''', (eventId, capacity, comments))
    conn.commit()

    rideId = c.lastrowid
    c.close()

    return (rideId, add_passenger(conn, rideId, driverName))

def list_rides(conn, eventId):
    if not event_exists(conn, eventId):
        raise Exception("Event DNE!")

    c = conn.cursor()
    c.execute('''select rowid, comments, capacity from rideList
where eventId is %d''' % eventId)

    ride_list = []

    for ride in c:
        print("ride: ")
        print(ride)
        d = conn.cursor()
        d.execute('select name, rowid from passengers where carId is %d' % ride[0])
        print("passengers: ")

        passenger_list = []

        for passenger in d:
            passenger_list.append({"id": passenger[1], "name": passenger[0]})
        d.close()

        ride_list.append({  "id": ride[0],
                            "comments": ride[1],
                            "capacity": ride[2],
                            "passengers": passenger_list
                            })
    c.close()

    return ride_list

def remove_ride(conn, carId):
    c = conn.cursor()
    c.execute('select rowid from passengers where carId is %d' % carId)
    for passenger in c:
        remove_passenger(conn, passenger)
    c.execute('delete from rideList where rowid is %d' % carId)

    conn.commit()

    c.close()

def ride_has_free_space(conn, carId):
    c = conn.cursor()
    c.execute('select capacity from rideList where rowid is %d' % carId)

    capacity = 0
    for results in c:
        capacity = results[0]

    i = 0
    c.execute('select * from passengers where carId is %d' % carId)
    for row in c:
        i += 1

    c.close()

    return i < capacity

def add_passenger(conn, rideId, name):
    if not ride_has_free_space(conn, rideId):
        raise Exception("Car is full!")

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

def main():
    app.run(debug=True)

if __name__ == "__main__":
    main()
