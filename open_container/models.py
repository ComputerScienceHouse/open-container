from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text

from open_container import db

class Event(db.Model):
    __tablename__ = 'eventList'
    id = Column(Integer, primary_key=True)
    startTime = Column(Text)
    endTime = Column(Text)
    host = Column(Text)
    name = Column(Text)
    description = Column(Text)

    def __init__(self, startTime, endTime, host, name, description):
        self.startTime = startTime
        self.endTime = endTime
        self.host = host
        self.name = name
        self.description = description


class Ride(db.Model):
    __tablename__ = 'rideList'
    id = Column(Integer, primary_key=True)
    eventId = Column(Integer)
    capacity = Column(Integer)
    comments = Column(Text)
    driver = Column(Text)
    departureTime = Column(Text)
    returnTime = Column(Text)

    def __init__(self, eventId, capacity, comments, driver, departureTime, returnTime):
        self.eventId = eventId
        self.capacity = capacity
        self.comments = comments
        self.driver = driver
        self.departureTime = departureTime
        self.returnTime = returnTime

class Passenger(db.Model):
    __tablename__ = 'passengersList'
    id = Column(Integer, primary_key=True)
    name = Column(Text)
    carId = Column(Integer)

    def __init__(self, name, carId):
        self.name = name
        self.carId = carId
