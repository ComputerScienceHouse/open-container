from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text

from open_container import db

class Event(db.Model):
    __tablename__ = 'eventList'
    id = Column(Integer, primary_key=True)
    startTime = Column(DateTime, nullable=False)
    endTime = Column(DateTime, nullable=False)
    host = Column(String(64), nullable=False)
    name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)

    def __init__(self, startTime, endTime, host, name, description):
        self.startTime = startTime
        self.endTime = endTime
        self.host = host
        self.name = name
        self.description = description


class Ride(db.Model):
    __tablename__ = 'rideList'
    id = Column(Integer, primary_key=True)
    eventId = Column(ForeignKey('eventList.id'), nullable=False)
    capacity = Column(Integer, nullable=False)
    comments = Column(Text, nullable=False)
    driver = Column(String(64), nullable=False)
    departureTime = Column(DateTime, nullable=False)
    returnTime = Column(DateTime, nullable=False)

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
    name = Column(String(64), nullable=False)
    carId = Column(ForeignKey('rideList.id'), nullable=False)

    def __init__(self, name, carId):
        self.name = name
        self.carId = carId
