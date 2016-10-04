from open_container.models import Event, Ride, Passenger
from datetime import datetime
from open_container import db
def add_event(startTime, endTime, name, description, host):
    event = Event(startTime, endTime, host, name, description)
    db.session.add(event)
    db.session.flush()
    db.session.commit()
    db.session.refresh(event)
    add_ride(event.id, "", 2 ** 16, "Need Ride", startTime, endTime)

    return event.id

def list_events(all_of_time=False):
    if all_of_time:
        events = [e for e in Event.query.filter()]
    else:
        events = [e for e in Event.query.filter(Event.startTime >=
            datetime.today())]

    return events

def get_event(id):
    return Event.query.filter(Event.id == id).first()

def event_exists(id):
    return not get_event(id) is None

def edit_event(id, name, description, start, end):
    Event.query.filter(Event.id == id).update(
        {
            'startTime': start,
            'endTime': end,
            'name': name,
            'description': description
        })
    db.session.flush()
    db.session.commit()
    return id

def remove_event(id):

    rides = Ride.query.filter(Ride.eventId == id)
    for ride in rides:
        remove_ride(ride.id)

    db.session.delete(Event.query.filter(Event.id == id).first())
    db.session.flush()
    db.session.commit()
    return None

def add_ride(eventId, comments, capacity, driverName, startTime, endTime):
    if not event_exists(eventId):
        raise EventExistenceError("Event DNE!")

    ride = Ride(eventId, capacity, comments, driverName, startTime, endTime)
    db.session.add(ride)
    db.session.flush()
    db.session.commit()
    db.session.refresh(ride)
    return ride.id

def list_rides(eventId):
    if not event_exists(eventId):
        raise EventExistenceError("Event DNE!")

    rides = Ride.query.filter(Ride.eventId == eventId)
    ride_list = []

    for ride in rides:
        passengers = Passenger.query.filter(Passenger.carId == ride.id)

        passenger_list = []

        for passenger in passengers:
            passenger_list.append({"id": passenger.id, "name": passenger.name})

        ride_list.append({  "id": ride.id,
                            "comments": ride.comments,
                            "capacity": ride.capacity,
                            "passengers": passenger_list,
                            "departureTime": ride.departureTime,
                            "returnTime": ride.returnTime,
                            "driver": ride.driver
                            })

    return ride_list

def list_attendees(eventId):
    rides = list_rides(eventId)

    passenger_names = []

    for ride in rides:
        passenger_names.append(ride['driver'])
        for passenger in ride['passengers']:
            passenger_names.append(passenger['name'])

    if "Need Ride" in passenger_names:
        passenger_names.remove("Need Ride")
    return passenger_names

def remove_ride(carId):
    passengers = Passenger.query.filter(Passenger.carId == carId)
    for passenger in passengers:
        remove_passenger(passenger)

    db.session.delete(Ride.query.filter(Ride.id == carId).first())
    db.session.flush()
    db.session.commit()

def ride_has_free_space(carId):
    capacity = Ride.query.filter(Ride.id == carId).first().capacity

    i = 0
    passengers = Passenger.query.filter(Passenger.carId == carId)
    for row in passengers:
        i += 1

    return i < capacity

def ride_is_empty(carId):
    i = 0
    passengers = Passenger.query.filter(Passenger.carId == carId)
    for row in passengers:
        i += 1

    return i == 0

def add_passenger(rideId, name):
    if not ride_has_free_space(rideId):
        raise CarFullError("Car is full!")

    passenger = Passenger(name, rideId)
    db.session.add(passenger)
    db.session.flush()
    db.session.commit()
    db.session.refresh(passenger)

    return passenger.id

def remove_passenger(passengerId):

    db.session.delete(Passenger.query.filter(Passenger.id ==
        passengerId).first())
    db.session.flush()
    db.session.commit()

def get_host_name(eventId):
    event = Event.query.filter(Event.id == eventId).first()

    if event:
        return event.host
    return ""

def get_driver_name(rideId):
    ride = Ride.query.filter(Ride.id == rideId).first()

    if ride:
        return ride.driver
    return ""

def get_passenger_name(passengerId):
    passenger = Passenger.query.filter(Passenger.id == passengerId).first()

    if passenger:
        return passenger.name
    return ""

def get_event_time(eventId):
    event = Event.query.filter(Event.id == eventId).first()

    if event:
        return event
    return None
