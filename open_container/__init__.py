import os
from datetime import datetime, date, timedelta, time
from flask import Flask, jsonify, make_response, render_template, request, send_from_directory, redirect
from random import shuffle
import sys
import json


from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

class CarFullError(Exception):
    pass

class EventExistenceError(Exception):
    pass

app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)
migrate = Migrate(app, db)
from open_container.database_helpers import *

@app.route('/js/<path:path>')
def serve_js(path):
    return send_from_directory(app.root_path + '/js',  path)

@app.route('/css/<path:path>')
def serve_css(path):
    return send_from_directory(app.root_path + '/css',  path)

@app.route('/list/event')
def http_list_event():

    event_list = []

    user_name = request.headers.get('X-WEBAUTH-USER')

    for event in list_events():
        attendees = list_attendees(event.id)
        shuffle(attendees)
        event_list.append(
            {
                'id': event.id,
                'attendees': attendees,
                'startTime': event.startTime,
                'endTime': event.endTime,
                'host': event.host,
                'name': event.name,
                'description': event.description
            })

    return render_template('list_event.html',
            events = event_list,
            user = user_name)

@app.route('/create/event')
def http_create_event():
    user_name = request.headers.get('X-WEBAUTH-USER')
    return render_template('create_event.html',
            user = user_name)

@app.route('/edit/event/<int:id>')
def http_edit_event(id):
    user_name = request.headers.get('X-WEBAUTH-USER')
    event = get_event(id)
    event_time = get_event_time(id)
    if user_name == event.host:
        return render_template('edit_event.html',
                user = user_name,
                event_id = id,
                event_name = event.name,
                event_description = event.description,
                event_startTime = event.startTime,
                event_endTime = event.startTime)
    else:
        return redirect('/view/event/' + str(id))

@app.route('/view/event/<int:id>')
def http_view_event(id):
    user_name = request.headers.get('X-WEBAUTH-USER')

    try:
        rides = list_rides( id)
        ride = get_event(id)
        host = ride.host
        description = ride.description
        event_name = get_event(id).name
    except EventExistenceError:
        return make_response(jsonify(
            {
                "code": 1,
                "error": "event DNE!"
            }),
            400)

    event_time = get_event_time(id)
    start_time = event_time.startTime
    end_time  = event_time.endTime

    return render_template('view_event.html',
            user = user_name,
            event = id,
            host = host,
            description = description,
            event_name = event_name,
            start_time = start_time,
            end_time = end_time,
            rides = rides)

@app.route('/')
def http_base():
    return http_list_event()

@app.route('/create/ride/<int:id>')
def http_create_ride(id):
    user_name = request.headers.get('X-WEBAUTH-USER')

    event_time = get_event_time(id)
    start_time = event_time.startTime
    end_time  = event_time.endTime

    return render_template('create_ride.html',
            user = user_name,
            start_time = start_time,
            end_time = end_time,
            event = id)

@app.route('/api/v1/<path:path>', methods=['POST'])
def api_deprecated():
    return make_response("API v1 is deprecated", 400)

@app.route('/api/v2/create/event', methods=['POST'])
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

    user_name = request.headers.get('X-WEBAUTH-USER')

    description = request.form['description']
    event_id = add_event(event_startTime, event_endTime, name,
                            description, user_name)

    return jsonify({"id":event_id})

@app.route('/api/v2/create/ride', methods=['POST'])
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

    user_name = request.headers.get('X-WEBAUTH-USER')

    try:
        ride_data = add_ride(event_id, comments, capacity, user_name,
ride_startTime, ride_endTime)
    except EventExistenceError:
        return make_response(jsonify(
            {
                "code": 1,
                "error": "event does not exist!"
            }),
            400)

    return jsonify({"rideId": ride_data})

@app.route('/api/v2/create/passenger', methods=['POST'])
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

    user_name = request.headers.get('X-WEBAUTH-USER')

    try:
        passenger_data = add_passenger(car_id, user_name)
    except CarFullError:
        return make_response(jsonify(
            {
                "code": 2,
                "error": "car is already full!"
            }),
            400)
    return jsonify({"id": passenger_data})

@app.route('/api/v2/edit/event', methods=['POST'])
def api_edit_event():

    try:
        event_id = int(request.form['event'])
    except ValueError:
        return make_response(jsonify(
            {
                "code": 4,
                "error": "event must be an integer value!"
            }),
            400)

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

    description = request.form['description']
    user_name = request.headers.get('X-WEBAUTH-USER')

    host_name = get_host_name(event_id)

    if user_name != host_name:
        return make_response(jsonify(
            {
                "code": 5,
                "error": "you are not that host!"
            }),
            400)

    edit_event(event_id, name, description,
                event_startTime, event_endTime)

    return make_response(str(event_id), 200)

@app.route('/api/v2/list/events', methods=['POST'])
def api_list_events():

    return jsonify({"events": list_events()})

@app.route('/api/v2/list/rides', methods=['POST'])
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
        return jsonify({"rides": list_rides(event_id)})
    except EventExistenceError:
        return make_response(jsonify(
            {
                "code": 1,
                "error": "event does not exist!"
            }),
            400)

@app.route('/api/v2/remove/event', methods=['POST'])
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

    host_name = get_host_name(event_id)

    if user_name != host_name:
        return make_response(jsonify(
            {
                "code": 5,
                "error": "you are not that host!"
            }),
            400)

    remove_event(event_id)

    return ""

@app.route('/api/v2/remove/ride', methods=['POST'])
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

    driver_name = get_driver_name(ride_id)

    if user_name != driver_name:
        return make_response(jsonify(
            {
                "code": 5,
                "error": "you are not that driver!"
            }),
            400)

    remove_ride(ride_id)

    return ""

@app.route('/api/v2/remove/passenger', methods=['POST'])
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

    passenger_name = get_passenger_name(passenger_id)

    print(passenger_name)
    print(user_name)
    if user_name != passenger_name:
        return make_response(jsonify(
            {
                "code": 5,
                "error": "you are not that passenger!"
            }),
            400)

    remove_passenger(passenger_id)

    return ""

def timestr_to_datetime(timestr):
    return datetime.strptime(timestr, "%Y-%m-%d %H:%M")

def datetime_to_timestr(date_time):
    return date_time.strftime("%Y-%m-%d %H:%M")
