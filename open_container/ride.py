import os
import MySQLdb as mdb
from datetime import datetime, date, timedelta, time
from flask import Flask, jsonify, make_response, render_template, request, send_from_directory
from random import shuffle
import sys
import json


json_config = None
with open(sys.argv[1]) as data_file:
    json_config = json.load(data_file)

class CarFullError(Exception):
    pass

class EventExistenceError(Exception):
    pass

def connect_db():    
    return mdb.connect(**json_config['mysql'])

def query_2(cursor, sql):
    global db_conn
    db_conn.ping(True)
    try:
        cursor.execute(sql)
    except Exception:
        db_conn = connect_db()
        cursor.execute(sql)

def query_3(cursor, sql, params):
    global db_conn
    db_conn.ping(True)
    try:
        cursor.execute(sql, params)
    except Exception:
        db_conn = connect_db()
        cursor.execute(sql, params)

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')

db_conn = None
DB_NAME = "test.db"
@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory(app.root_path + '/js',  path)

@app.route('/css/<path:path>')
def serve_css(path):
    return send_from_directory(app.root_path + '/css',  path)

@app.route('/list/event')
def http_list_event():

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
    user_name = request.headers.get('X-WEBAUTH-USER')

    try:
        id = int(id)
    except ValueError:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "input not an integer!"
            }),
            400)
    try:
        rides = list_rides(db_conn, id)
        ride = get_event(db_conn, id)
        host = ride[3]
        description = ride[5]
        event_name = get_event(db_conn, id)[4]
    except EventExistenceError:
        return make_response(jsonify(
            {
                "code": 1,
                "error": "event DNE!"
            }),
            400)

    return render_template('edit_event.html',
            user = user_name,
            event = id,
            host = host,
            description = description,
            event_name = event_name,
            rides = rides)

@app.route('/')
def http_base():
    return http_list_event()

@app.route('/create/ride/<id>')
def http_create_ride(id):
    user_name = request.headers.get('X-WEBAUTH-USER')

    try:
        id = int(id)
    except ValueError:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "input not an integer!"
            }),
            400)

    return render_template('create_ride.html',
            user = user_name,
            event = id)

@app.route('/api/v1/create/event', methods=['POST'])
def api_create_event():
 
    try:
        event_startTime = request.form['startTime']
        event_endTime = request.form['endTime']
    except ValueError:
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

    error = None

    try:
        ride_startTime = request.form['departureTime']
        ride_endTime = request.form['returnTime']
    except ValueError:
        return make_response(jsonify(
            {
                "code": 2,
                "error": "invalid time format!"
            }),
            400)

    try:
        event_id = int(request.form['eventId'])
    except ValueError:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "eventId must be an integer value!"
            }),
            400)

    comments = request.form['comments']

    try:
        capacity = int(request.form['capacity'])
        if capacity <= 0:
            raise CarFullError("< 0!")
    except ValueError:
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
    except EventExistenceError:
        return make_response(jsonify(
            {
                "code": 1,
                "error": "event does not exist!"
            }),
            400)

    return jsonify({"rideId": ride_data})

@app.route('/api/v1/create/passenger', methods=['POST'])
def api_create_passenger():

    error = None

    try:
        car_id = int(request.form['carId'])
    except ValueError:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "carId must be an integer value greater than 0!"
            }),
            400)

    name = request.form['name']

    try:
        passenger_data = add_passenger(db_conn, car_id, name)
    except CarFullError:
        return make_response(jsonify(
            {
                "code": 2,
                "error": "car is already full!"
            }),
            400)

    return jsonify({"id": passenger_data})

@app.route('/api/v1/list/events', methods=['POST'])
def api_list_events():

    return jsonify({"events": list_events(db_conn)})

@app.route('/api/v1/list/rides', methods=['POST'])
def api_list_rides():

    try:
        event_id = int(request.form['id'])
    except ValueError:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "eventId must be an integer value greater than 0!"
            }),
            400)

    try:
        return jsonify({"rides": list_rides(db_conn, event_id)})
    except EventExistenceError:
        return make_response(jsonify(
            {
                "code": 1,
                "error": "event does not exist!"
            }),
            400)

@app.route('/api/v1/remove/event', methods=['POST'])
def api_remove_event():

    try:
        event_id = int(request.form['eventId'])
    except ValueError:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "eventId must be an integer value!"
            }),
            400)

    user_name = request.headers.get('X-WEBAUTH-USER')

    host_name = get_host_name(db_conn, event_id)

    if user_name != host_name:
        return make_response(jsonify(
            {
                "code": 5,
                "error": "you are not that host!"
            }),
            400)

    remove_event(db_conn, event_id)

    return ""

@app.route('/api/v1/remove/ride', methods=['POST'])
def api_remove_ride():

    try:
        ride_id = int(request.form['id'])
    except ValueError:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "rideId must be an integer value!"
            }),
            400)

    user_name = request.headers.get('X-WEBAUTH-USER')

    driver_name = get_driver_name(db_conn, ride_id)

    if user_name != driver_name:
        return make_response(jsonify(
            {
                "code": 5,
                "error": "you are not that driver!"
            }),
            400)

    remove_ride(db_conn, ride_id)

    return ""

@app.route('/api/v1/remove/passenger', methods=['POST'])
def api_remove_passenger():

    try:
        passenger_id = int(request.form['id'])
    except ValueError:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "passengerId must be an integer value!"
            }),
            400)

    user_name = request.headers.get('X-WEBAUTH-USER')

    passenger_name = get_passenger_name(db_conn, passenger_id)

    print(passenger_name)
    print(user_name)
    if user_name != passenger_name:
        return make_response(jsonify(
            {
                "code": 5,
                "error": "you are not that passenger!"
            }),
            400)

    remove_passenger(db_conn, passenger_id)

    return ""

def timestr_to_datetime(timestr):
    return datetime.strptime(timestr, "%Y-%m-%d %H:%M")

def datetime_to_timestr(date_time):
    return date_time.strftime("%Y-%m-%d %H:%M")

def create_database():
    db_conn = connect_db()

    # tables
    print("creating database")
    c = db_conn.cursor()

    query_2(c, '''create table eventList
(rowid INT NOT NULL AUTO_INCREMENT PRIMARY KEY, startTime text, endTime text, host text, name text, description text)''')
    query_2(c, '''create table rideList
(rowid INT NOT NULL AUTO_INCREMENT PRIMARY KEY, eventId integer, capacity integer, comments text, driver text, departureTime text, returnTime text)''')
    query_2(c, '''create table passengers
(rowid INT NOT NULL AUTO_INCREMENT PRIMARY KEY, name text, carid integer)''')

    db_conn.commit()

    c.close()
    print("created database")

def add_event(conn, startTime, endTime, name, description, host):
    c = conn.cursor()

    print(startTime, endTime, name, description, host)
    query_3(c, '''insert into eventList (startTime, endTime, host, name, description)
values (%s, %s, %s, %s, %s)''', (startTime, endTime, host, name, description))

    conn.commit()

    c.close()

    add_ride(conn, c.lastrowid, "", 2 ** 16, "Need Ride", startTime, endTime)

    return c.lastrowid

def list_events(conn, all_of_time=False):
    c = conn.cursor()

    query_2(c, '''select startTime, endTime, host, name, description, rowid from
eventList order by endTime''')

    events = []

    for row in c:
        print(row[0])
        t = datetime.strptime(row[0].strip('\''), "%Y-%m-%d %H:%M")
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
    query_2(c, '''select * from eventList where rowid=%d''' % id)

    for row in c:
        c.close()
        return row

    c.close()
    return None

def event_exists(conn, id):
    return not get_event(conn, id) is None

def remove_event(conn, id):
    c = conn.cursor()
    query_2(c, 'delete from eventList where rowid=%d' % id)

    conn.commit()

    query_2(c, 'select rowid from rideList where eventId=%d' % id)
    for ride in c:
        remove_ride(conn, ride[0])

    c.close()
    return None

def add_ride(conn, eventId, comments, capacity, driverName, startTime, endTime):
    if not event_exists(conn, eventId):
        raise EventExistenceError("Event DNE!")

    c = conn.cursor()
    query_3(c, '''insert into rideList (eventId, capacity, comments, driver, departureTime, returnTime) values (%s, %s, %s, %s, %s, %s)''', (eventId, capacity, comments, driverName, startTime, endTime))

    conn.commit()

    c.close()

    return c.lastrowid

def list_rides(conn, eventId):
    if not event_exists(conn, eventId):
        raise EventExistenceError("Event DNE!")

    c = conn.cursor()
    query_2(c, '''select rowid, comments, capacity, departureTime, returnTime, driver from rideList where eventId=%d''' % eventId)

    ride_list = []

    for ride in c:
        d = conn.cursor()
        query_2(d, 'select name, rowid from passengers where carId=%d' % ride[0])

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
    query_2(c, 'select rowid from passengers where carId=%d' % carId)
    for passenger in c:
        remove_passenger(conn, passenger)
    query_2(c, 'delete from rideList where rowid=%d' % carId)

    conn.commit()

    c.close()

def ride_has_free_space(conn, carId):
    c = conn.cursor()
    query_2(c, 'select capacity from rideList where rowid=%d' % carId)

    capacity = 0
    for results in c:
        capacity = results[0]

    i = 0
    query_2(c, 'select * from passengers where carId=%d' % carId)
    for row in c:
        i += 1

    c.close()

    return i < capacity

def ride_is_empty(conn, carId): 
    i = 0
    c = conn.cursor()
    query_2(c, 'select * from passengers where carId=%d' % carId)
    for row in c:
        i += 1

    c.close()

    print("passenger cont: ", i)
    return i == 0

def add_passenger(conn, rideId, name):
    if not ride_has_free_space(conn, rideId):
        raise CarFullError("Car is full!")

    c = conn.cursor()
    print(name, rideId)
    query_3(c, '''insert into passengers (name, carid) values (%s, %s)''', (name, rideId))

    c.close()

    conn.commit()
    return c.lastrowid

def remove_passenger(conn, passengerId):
    rideId = 0
    c = conn.cursor()
    query_2(c, 'select carId from passengers where rowid=%d' %passengerId)

    for car in c:
        rideId = car[0]

    print("rideId: ", rideId)

    query_2(c, 'delete from passengers where rowid=%d' % passengerId)
    conn.commit()

    #if ride_is_empty(conn, rideId):
    #    remove_ride(conn, rideId)

    c.close()

def get_host_name(conn, eventId):
    c = conn.cursor()
    query_2(c, '''select host from eventList where rowid=%d''' % eventId)

    for event in c:
        return event[0]
    return ""

def get_driver_name(conn, rideId):

    c = conn.cursor()
    query_2(c, '''select driver from rideList where rowid=%d''' % rideId)

    for car in c:
        return car[0]
    return ""

def get_passenger_name(conn, passengerId):
    c = conn.cursor()
    query_2(c, 'select name from passengers where rowid=%d' % passengerId)

    for name in c:
        return name[0]
    return ""

def main():
    global db_conn

    db_conn = connect_db()

    app.run(debug=json_config['debug'], port=json_config['port'])

if __name__ == "__main__":
    main()
