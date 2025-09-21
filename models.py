from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Index, func
import uuid

db = SQLAlchemy()

class Airport(db.Model):
    """Airport information"""
    __tablename__ = 'airports'
    
    id = db.Column(db.Integer, primary_key=True)
    iata_code = db.Column(db.String(3), unique=True, nullable=False, index=True)
    icao_code = db.Column(db.String(4), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(100), nullable=False)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)
    timezone = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    origin_flights = db.relationship('Flight', foreign_keys='Flight.origin_airport_id', backref='origin_airport', lazy='dynamic')
    destination_flights = db.relationship('Flight', foreign_keys='Flight.destination_airport_id', backref='destination_airport', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'iata_code': self.iata_code,
            'icao_code': self.icao_code,
            'name': self.name,
            'city': self.city,
            'state': self.state,
            'country': self.country,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timezone': self.timezone
        }

class Airline(db.Model):
    """Airline information"""
    __tablename__ = 'airlines'
    
    id = db.Column(db.Integer, primary_key=True)
    iata_code = db.Column(db.String(2), unique=True, nullable=False, index=True)
    icao_code = db.Column(db.String(3), unique=True, nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    callsign = db.Column(db.String(100), nullable=True)
    country = db.Column(db.String(100), nullable=False)
    logo_url = db.Column(db.String(500), nullable=True)
    website_url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    flights = db.relationship('Flight', backref='airline', lazy='dynamic')
    aircraft = db.relationship('Aircraft', backref='airline', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'iata_code': self.iata_code,
            'icao_code': self.icao_code,
            'name': self.name,
            'callsign': self.callsign,
            'country': self.country,
            'logo_url': self.logo_url,
            'website_url': self.website_url
        }

class Aircraft(db.Model):
    """Aircraft type information"""
    __tablename__ = 'aircraft'
    
    id = db.Column(db.Integer, primary_key=True)
    type_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    manufacturer = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(100), nullable=False)
    variant = db.Column(db.String(50), nullable=True)
    capacity = db.Column(db.Integer, nullable=True)
    range_km = db.Column(db.Integer, nullable=True)
    cruise_speed_kmh = db.Column(db.Integer, nullable=True)
    airline_id = db.Column(db.Integer, db.ForeignKey('airlines.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    flights = db.relationship('Flight', backref='aircraft', lazy='dynamic')

    def to_dict(self):
        return {
            'id': self.id,
            'type_code': self.type_code,
            'manufacturer': self.manufacturer,
            'model': self.model,
            'variant': self.variant,
            'capacity': self.capacity,
            'range_km': self.range_km,
            'cruise_speed_kmh': self.cruise_speed_kmh
        }

class Flight(db.Model):
    """Flight information"""
    __tablename__ = 'flights'
    
    id = db.Column(db.Integer, primary_key=True)
    flight_number = db.Column(db.String(10), nullable=False, index=True)
    airline_id = db.Column(db.Integer, db.ForeignKey('airlines.id'), nullable=False)
    aircraft_id = db.Column(db.Integer, db.ForeignKey('aircraft.id'), nullable=False)
    origin_airport_id = db.Column(db.Integer, db.ForeignKey('airports.id'), nullable=False)
    destination_airport_id = db.Column(db.Integer, db.ForeignKey('airports.id'), nullable=False)
    
    # Flight times
    scheduled_departure = db.Column(db.DateTime, nullable=False, index=True)
    actual_departure = db.Column(db.DateTime, nullable=True)
    scheduled_arrival = db.Column(db.DateTime, nullable=False)
    actual_arrival = db.Column(db.DateTime, nullable=True)
    
    # Flight status and details
    gate = db.Column(db.String(10), nullable=True)
    terminal = db.Column(db.String(10), nullable=True)
    status = db.Column(db.String(20), nullable=False, index=True)  # ON_TIME, DELAYED, CANCELLED, BOARDING, etc.
    delay_minutes = db.Column(db.Integer, default=0)
    cancellation_reason = db.Column(db.String(255), nullable=True)
    
    # Passenger and capacity info
    seats_available = db.Column(db.Integer, nullable=True)
    total_seats = db.Column(db.Integer, nullable=True)
    load_factor = db.Column(db.Float, nullable=True)
    
    # Predictive data
    on_time_probability = db.Column(db.Float, nullable=True)
    delay_probability = db.Column(db.Float, nullable=True)
    cancellation_probability = db.Column(db.Float, nullable=True)
    
    # Pricing info
    base_price = db.Column(db.Float, nullable=True)
    current_price = db.Column(db.Float, nullable=True)
    currency = db.Column(db.String(3), default='USD')
    
    # Additional metadata
    flight_date = db.Column(db.Date, nullable=False, index=True)
    duration_minutes = db.Column(db.Integer, nullable=True)
    distance_miles = db.Column(db.Integer, nullable=True)
    route_frequency = db.Column(db.String(20), nullable=True)  # DAILY, WEEKLY, etc.
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Indexes for better query performance
    __table_args__ = (
        Index('idx_flight_date_origin', 'flight_date', 'origin_airport_id'),
        Index('idx_flight_date_destination', 'flight_date', 'destination_airport_id'),
        Index('idx_flight_route_date', 'origin_airport_id', 'destination_airport_id', 'flight_date'),
        Index('idx_status_date', 'status', 'flight_date'),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'flight_number': self.flight_number,
            'airline': self.airline.to_dict() if self.airline else None,
            'aircraft': self.aircraft.to_dict() if self.aircraft else None,
            'origin_airport': self.origin_airport.to_dict() if self.origin_airport else None,
            'destination_airport': self.destination_airport.to_dict() if self.destination_airport else None,
            'scheduled_departure': self.scheduled_departure.isoformat() if self.scheduled_departure else None,
            'actual_departure': self.actual_departure.isoformat() if self.actual_departure else None,
            'scheduled_arrival': self.scheduled_arrival.isoformat() if self.scheduled_arrival else None,
            'actual_arrival': self.actual_arrival.isoformat() if self.actual_arrival else None,
            'gate': self.gate,
            'terminal': self.terminal,
            'status': self.status,
            'delay_minutes': self.delay_minutes,
            'cancellation_reason': self.cancellation_reason,
            'seats_available': self.seats_available,
            'total_seats': self.total_seats,
            'load_factor': self.load_factor,
            'on_time_probability': self.on_time_probability,
            'delay_probability': self.delay_probability,
            'cancellation_probability': self.cancellation_probability,
            'base_price': self.base_price,
            'current_price': self.current_price,
            'currency': self.currency,
            'flight_date': self.flight_date.isoformat() if self.flight_date else None,
            'duration_minutes': self.duration_minutes,
            'distance_miles': self.distance_miles,
            'route_frequency': self.route_frequency
        }

class FlightStatus(db.Model):
    """Real-time flight status updates"""
    __tablename__ = 'flight_status'
    
    id = db.Column(db.Integer, primary_key=True)
    flight_id = db.Column(db.Integer, db.ForeignKey('flights.id'), nullable=False)
    status = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    delay_minutes = db.Column(db.Integer, default=0)
    gate = db.Column(db.String(10), nullable=True)
    terminal = db.Column(db.String(10), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # Relationships
    flight = db.relationship('Flight', backref='status_updates')

    def to_dict(self):
        return {
            'id': self.id,
            'flight_id': self.flight_id,
            'status': self.status,
            'timestamp': self.timestamp.isoformat(),
            'delay_minutes': self.delay_minutes,
            'gate': self.gate,
            'terminal': self.terminal,
            'notes': self.notes
        }

class Route(db.Model):
    """Flight routes and their statistics"""
    __tablename__ = 'routes'
    
    id = db.Column(db.Integer, primary_key=True)
    origin_airport_id = db.Column(db.Integer, db.ForeignKey('airports.id'), nullable=False)
    destination_airport_id = db.Column(db.Integer, db.ForeignKey('airports.id'), nullable=False)
    airline_id = db.Column(db.Integer, db.ForeignKey('airlines.id'), nullable=True)
    
    # Route statistics
    average_duration_minutes = db.Column(db.Integer, nullable=True)
    distance_miles = db.Column(db.Integer, nullable=True)
    on_time_percentage = db.Column(db.Float, nullable=True)
    average_delay_minutes = db.Column(db.Float, nullable=True)
    flight_frequency = db.Column(db.String(20), nullable=True)  # DAILY, WEEKLY, etc.
    typical_aircraft_types = db.Column(db.Text, nullable=True)  # JSON array of aircraft types
    
    # Route metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    origin_airport = db.relationship('Airport', foreign_keys=[origin_airport_id], backref='origin_routes')
    destination_airport = db.relationship('Airport', foreign_keys=[destination_airport_id], backref='destination_routes')
    airline = db.relationship('Airline', backref='routes')

    def to_dict(self):
        return {
            'id': self.id,
            'origin_airport': self.origin_airport.to_dict() if self.origin_airport else None,
            'destination_airport': self.destination_airport.to_dict() if self.destination_airport else None,
            'airline': self.airline.to_dict() if self.airline else None,
            'average_duration_minutes': self.average_duration_minutes,
            'distance_miles': self.distance_miles,
            'on_time_percentage': self.on_time_percentage,
            'average_delay_minutes': self.average_delay_minutes,
            'flight_frequency': self.flight_frequency,
            'typical_aircraft_types': self.typical_aircraft_types,
            'is_active': self.is_active
        }

class Weather(db.Model):
    """Weather data for airports"""
    __tablename__ = 'weather'
    
    id = db.Column(db.Integer, primary_key=True)
    airport_id = db.Column(db.Integer, db.ForeignKey('airports.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, index=True)
    hour = db.Column(db.Integer, nullable=False)  # 0-23
    
    # Weather conditions
    temperature_celsius = db.Column(db.Float, nullable=True)
    humidity_percent = db.Column(db.Float, nullable=True)
    wind_speed_mph = db.Column(db.Float, nullable=True)
    wind_direction_degrees = db.Column(db.Float, nullable=True)
    visibility_miles = db.Column(db.Float, nullable=True)
    precipitation_inches = db.Column(db.Float, nullable=True)
    conditions = db.Column(db.String(50), nullable=True)  # CLEAR, CLOUDY, RAIN, SNOW, etc.
    
    # Impact on flights
    delay_factor = db.Column(db.Float, nullable=True)  # 0.0 to 2.0 multiplier
    cancellation_risk = db.Column(db.Float, nullable=True)  # 0.0 to 1.0 probability
    
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    airport = db.relationship('Airport', backref='weather_data')

    def to_dict(self):
        return {
            'id': self.id,
            'airport_id': self.airport_id,
            'date': self.date.isoformat(),
            'hour': self.hour,
            'temperature_celsius': self.temperature_celsius,
            'humidity_percent': self.humidity_percent,
            'wind_speed_mph': self.wind_speed_mph,
            'wind_direction_degrees': self.wind_direction_degrees,
            'visibility_miles': self.visibility_miles,
            'precipitation_inches': self.precipitation_inches,
            'conditions': self.conditions,
            'delay_factor': self.delay_factor,
            'cancellation_risk': self.cancellation_risk
        }
