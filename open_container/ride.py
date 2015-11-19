import os
import sqlite3
from datetime import datetime, date, timedelta, time
from flask import Flask, jsonify, make_response, render_template, request, send_from_directory
from random import shuffle
import sys

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')

DB_NAME = "test.db"
@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory(app.root_path + '/js',  path)

@app.route('/css/<path:path>')
def serve_css(path):
    return send_from_directory(app.root_path + '/css',  path)

@app.route('/list/event')
def http_list_event():
    db_conn = load_database(DB_NAME)

    event_list = list_events(db_conn)

    user_name = request.headers.get('X-WEBAUTH-USER')

    for event in event_list:
        attendees = list_attendees(db_conn, event['id'])
        shuffle(attendees)
        event['attendees'] = attendees

    return render_template('list_event.html',
            events = event_list,
            user = user_name)

@app.route('/create/event')
def http_create_event():
    user_name = request.headers.get('X-WEBAUTH-USER')
    return render_template('create_event.html',
            user = user_name)

@app.route('/edit/event/<id>')
def http_edit_event(id):
    db_conn = load_database(DB_NAME)
    user_name = request.headers.get('X-WEBAUTH-USER')

    rides = list_rides(db_conn, int(id))

    host = get_event(db_conn, int(id))[2]

    event_name = get_event(db_conn, int(id))[3]

    return render_template('edit_event.html',
            user = user_name,
            event = id,
            host = host,
            event_name = event_name,
            rides = rides)

@app.route('/')
def http_base():
    return http_list_event()

@app.route('/create/ride/<id>')
def http_create_ride(id):
    db_conn = load_database(DB_NAME)
    user_name = request.headers.get('X-WEBAUTH-USER')

    return render_template('create_ride.html',
            user = user_name,
            event = id)

@app.route('/api/v1/create/event', methods=['POST'])
def api_create_event():
    db_conn = load_database(DB_NAME)
 

    try:
        event_startTime = timestr_to_datetime(request.form['startTime'])
        event_endTime = timestr_to_datetime(request.form['endTime'])
    except Exception:
        return make_response(jsonify(
            {
                "code": 2,
                "error": "invalid time format!"
            }),
            400)

    name = request.form['name']
    if name == "":
        return make_response(jsonify(
            {
                "code": 3,
                "error": "empty string not accepted for name!"
            }),
            400)

    user = request.form['driver']
    if user == "":
        return make_response(jsonify(
            {
                "code": 3,
                "error": "empty string not accepted for name!"
            }),
            400)

    description = request.form['description']
    event_id = add_event(db_conn, event_startTime, event_endTime, name,
description, user)

    return jsonify({"id":event_id})

@app.route('/api/v1/create/ride', methods=['POST'])
def api_create_ride():
    db_conn = load_database(DB_NAME)

    error = None

    try:
        ride_startTime = timestr_to_datetime(request.form['departureTime'])
        ride_endTime = timestr_to_datetime(request.form['returnTime'])
    except Exception:
        return make_response(jsonify(
            {
                "code": 2,
                "error": "invalid time format!"
            }),
            400)

    try:
        event_id = int(request.form['eventId'])
    except Exception:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "eventId must be an integer value!"
            }),
            400)

    comments = request.form['comments']

    try:
        capacity = int(request.form['capacity'])
    except Exception:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "capacity must be an integer value greater than 0!"
            }),
            400)

    driver_name = request.form['driverName']

    try:
        ride_data = add_ride(db_conn, event_id, comments, capacity, driver_name,
ride_startTime, ride_endTime)
    except Exception:
        return make_response(jsonify(
            {
                "code": 1,
                "error": "event does not exist!"
            }),
            400)

    return jsonify({"rideId": ride_data})

@app.route('/api/v1/create/passenger', methods=['POST'])
def api_create_passenger():
    db_conn = load_database(DB_NAME)

    error = None

    try:
        car_id = int(request.form['carId'])
    except Exception:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "carId must be an integer value greater than 0!"
            }),
            400)

    name = request.form['name']

    try:
        passenger_data = add_passenger(db_conn, car_id, name)
    except Exception:
        return make_response(jsonify(
            {
                "code": 2,
                "error": "car is already full!"
            }),
            400)

    return jsonify({"id": passenger_data})

@app.route('/api/v1/list/events', methods=['POST'])
def api_list_events():
    db_conn = load_database(DB_NAME)

    return jsonify({"events": list_events(db_conn)})

@app.route('/api/v1/list/rides', methods=['POST'])
def api_list_rides():
    db_conn = load_database(DB_NAME)

    try:
        event_id = int(request.form['id'])
    except Exception:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "eventId must be an integer value greater than 0!"
            }),
            400)

    try:
        return jsonify({"rides": list_rides(db_conn, event_id)})
    except Exception:
        return make_response(jsonify(
            {
                "code": 1,
                "error": "event does not exist!"
            }),
            400)

@app.route('/api/v1/remove/event', methods=['POST'])
def api_remove_event():
    db_conn = load_database(DB_NAME)

    try:
        event_id = int(request.form['eventId'])
    except Exception:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "eventId must be an integer value!"
            }),
            400)

    remove_event(db_conn, event_id)

    return ""

@app.route('/api/v1/remove/ride', methods=['POST'])
def api_remove_ride():
    db_conn = load_database(DB_NAME)

    try:
        ride_id = int(request.form['id'])
    except Exception:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "rideId must be an integer value!"
            }),
            400)

    remove_ride(db_conn, ride_id)

    return ""

@app.route('/api/v1/remove/passenger', methods=['POST'])
def api_remove_passenger():
    db_conn = load_database(DB_NAME)

    try:
        passenger_id = int(request.form['id'])
    except Exception:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "passengerId must be an integer value!"
            }),
            400)

    remove_passenger(db_conn, passenger_id)

    return ""

def timestr_to_datetime(timestr):
    return datetime.strptime(timestr, "%Y-%m-%d %H:%M:%S")

def datetime_to_timestr(date_time):
    return date_time.strftime("%Y-%m-%d %H:%M:%S")

def create_database(file_name):
    conn = sqlite3.connect(file_name)

    # tables
    c = conn.cursor()

    c.execute('''create table eventList
(startTime datetime, endTime datetime, host text, name text, description text)''')
    c.execute('''create table rideList
(eventId integer, capacity integer, comments text, driver text, departureTime datetime, returnTime datetime)''')
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

def add_event(conn, startTime, endTime, name, description, host):
    c = conn.cursor()

    c.execute('''insert into eventList (startTime, endTime, host, name, description)
values (?, ?, ?, ?, ?)''', (startTime, endTime, host, name, description))

    conn.commit()

    c.close()

    add_ride(conn, c.lastrowid, "", 2 ** 32, "Need Ride", startTime, endTime)

    return c.lastrowid

def list_events(conn, all_of_time=False):
    c = conn.cursor()

    c.execute('''select startTime, endTime, host, name, description, rowid from
eventList order by endTime''')

    events = []

    for row in c:
        t = datetime.strptime(row[0].split('.')[0], "%Y-%m-%d %H:%M:%S")
        # just check it against the date for now, more precision comes later
        if not all_of_time and t.date() < date.today():
            continue
        events.append({"id": row[5], "startTime": row[0], "name": row[3],
"description": row[4], "endTime": row[1], "host": row[2]})
        print(row)

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
        remove_ride(conn, ride[0])

    c.close()
    return None

def add_ride(conn, eventId, comments, capacity, driverName, startTime, endTime):
    if not event_exists(conn, eventId):
        raise Exception("Event DNE!")

    c = conn.cursor()
    c.execute('''insert into rideList (eventId, capacity, comments, driver,
departureTime, returnTIme)
values (?, ?, ?, ?, ?, ?)''', (eventId, capacity, comments, driverName,
startTime, endTime))

    conn.commit()

    c.close()

    return c.lastrowid

def list_rides(conn, eventId):
    if not event_exists(conn, eventId):
        raise Exception("Event DNE!")

    c = conn.cursor()
    c.execute('''select rowid, comments, capacity, departureTime, returnTime, driver from rideList where eventId is %d''' % eventId)

    ride_list = []

    for ride in c:
        d = conn.cursor()
        d.execute('select name, rowid from passengers where carId is %d' % ride[0])

        passenger_list = []

        for passenger in d:
            passenger_list.append({"id": passenger[1], "name": passenger[0]})
        d.close()

        ride_list.append({  "id": ride[0],
                            "comments": ride[1],
                            "capacity": ride[2],
                            "passengers": passenger_list,
                            "departureTime": ride[3],
                            "returnTime": ride[4],
                            "driver": ride[5]
                            })
    c.close()

    return ride_list

def list_attendees(conn, eventId):
    rides = list_rides(conn, eventId)

    passenger_names = []

    for ride in rides:
        passenger_names.append(ride['driver'])
        for passenger in ride['passengers']:
            passenger_names.append(passenger['name'])

    passenger_names.remove("Need Ride")
    return passenger_names

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

def ride_is_empty(conn, carId): 
    i = 0
    c = conn.cursor()
    c.execute('select * from passengers where carId is %d' % carId)
    for row in c:
        i += 1

    c.close()

    print("passenger cont: ", i)
    return i == 0

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
    rideId = 0
    c = conn.cursor()
    c.execute('select carId from passengers where rowid is %d' %passengerId)

    for car in c:
        rideId = car[0]

    print("rideId: ", rideId)

    c.execute('delete from passengers where rowid is %d' % passengerId)
    conn.commit()

    #if ride_is_empty(conn, rideId):
    #    remove_ride(conn, rideId)

    c.close()

def main():
    app.run(debug=True, port=64957)

if __name__ == "__main__":
    main()
