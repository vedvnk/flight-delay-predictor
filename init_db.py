#!/usr/bin/env python3
"""
Database initialization script for OnTime flight prediction system.
This script creates the database, tables, and populates them with initial data.
"""

import os
import sys
import pandas as pd
from datetime import datetime, timedelta
import sqlite3
from sqlalchemy import create_engine, text
from models import db, Airport, Airline, Aircraft, Flight, FlightStatus, Route, Weather

def create_app():
    """Create Flask app for database initialization"""
    from flask import Flask
    
    app = Flask(__name__)
    
    # Database configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ontime.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    return app

def init_database():
    """Initialize the database with tables"""
    print("Creating database tables...")
    
    with app.app_context():
        # Create all tables
        db.create_all()
        print("✅ Database tables created successfully")

def populate_airports():
    """Populate airports with major US airports"""
    print("Populating airports...")
    
    airports_data = [
        {
            'iata_code': 'LAX',
            'icao_code': 'KLAX',
            'name': 'Los Angeles International Airport',
            'city': 'Los Angeles',
            'state': 'California',
            'country': 'United States',
            'latitude': 33.9425,
            'longitude': -118.4081,
            'timezone': 'America/Los_Angeles'
        },
        {
            'iata_code': 'ORD',
            'icao_code': 'KORD',
            'name': 'Chicago O\'Hare International Airport',
            'city': 'Chicago',
            'state': 'Illinois',
            'country': 'United States',
            'latitude': 41.9786,
            'longitude': -87.9048,
            'timezone': 'America/Chicago'
        },
        {
            'iata_code': 'JFK',
            'icao_code': 'KJFK',
            'name': 'John F. Kennedy International Airport',
            'city': 'New York',
            'state': 'New York',
            'country': 'United States',
            'latitude': 40.6413,
            'longitude': -73.7781,
            'timezone': 'America/New_York'
        },
        {
            'iata_code': 'LGA',
            'icao_code': 'KLGA',
            'name': 'LaGuardia Airport',
            'city': 'New York',
            'state': 'New York',
            'country': 'United States',
            'latitude': 40.7769,
            'longitude': -73.8740,
            'timezone': 'America/New_York'
        },
        {
            'iata_code': 'ATL',
            'icao_code': 'KATL',
            'name': 'Hartsfield-Jackson Atlanta International Airport',
            'city': 'Atlanta',
            'state': 'Georgia',
            'country': 'United States',
            'latitude': 33.6407,
            'longitude': -84.4277,
            'timezone': 'America/New_York'
        },
        {
            'iata_code': 'DFW',
            'icao_code': 'KDFW',
            'name': 'Dallas/Fort Worth International Airport',
            'city': 'Dallas',
            'state': 'Texas',
            'country': 'United States',
            'latitude': 32.8968,
            'longitude': -97.0380,
            'timezone': 'America/Chicago'
        },
        {
            'iata_code': 'DEN',
            'icao_code': 'KDEN',
            'name': 'Denver International Airport',
            'city': 'Denver',
            'state': 'Colorado',
            'country': 'United States',
            'latitude': 39.8561,
            'longitude': -104.6737,
            'timezone': 'America/Denver'
        },
        {
            'iata_code': 'SFO',
            'icao_code': 'KSFO',
            'name': 'San Francisco International Airport',
            'city': 'San Francisco',
            'state': 'California',
            'country': 'United States',
            'latitude': 37.6213,
            'longitude': -122.3790,
            'timezone': 'America/Los_Angeles'
        },
        {
            'iata_code': 'SEA',
            'icao_code': 'KSEA',
            'name': 'Seattle-Tacoma International Airport',
            'city': 'Seattle',
            'state': 'Washington',
            'country': 'United States',
            'latitude': 47.4502,
            'longitude': -122.3088,
            'timezone': 'America/Los_Angeles'
        },
        {
            'iata_code': 'LAS',
            'icao_code': 'KLAS',
            'name': 'Harry Reid International Airport',
            'city': 'Las Vegas',
            'state': 'Nevada',
            'country': 'United States',
            'latitude': 36.0840,
            'longitude': -115.1537,
            'timezone': 'America/Los_Angeles'
        }
    ]
    
    with app.app_context():
        for airport_data in airports_data:
            airport = Airport(**airport_data)
            db.session.add(airport)
        
        db.session.commit()
        print(f"✅ Added {len(airports_data)} airports")

def populate_airlines():
    """Populate airlines with major US carriers"""
    print("Populating airlines...")
    
    airlines_data = [
        {
            'iata_code': 'AA',
            'icao_code': 'AAL',
            'name': 'American Airlines',
            'callsign': 'American',
            'country': 'United States',
            'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0f/American_Airlines_logo_2019.svg/200px-American_Airlines_logo_2019.svg.png',
            'website_url': 'https://www.aa.com'
        },
        {
            'iata_code': 'UA',
            'icao_code': 'UAL',
            'name': 'United Airlines',
            'callsign': 'United',
            'country': 'United States',
            'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/5/57/United_Airlines_logo_2010.svg/200px-United_Airlines_logo_2010.svg.png',
            'website_url': 'https://www.united.com'
        },
        {
            'iata_code': 'DL',
            'icao_code': 'DAL',
            'name': 'Delta Air Lines',
            'callsign': 'Delta',
            'country': 'United States',
            'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8b/Delta_Airlines_logo_2019.svg/200px-Delta_Airlines_logo_2019.svg.png',
            'website_url': 'https://www.delta.com'
        },
        {
            'iata_code': 'WN',
            'icao_code': 'SWA',
            'name': 'Southwest Airlines',
            'callsign': 'Southwest',
            'country': 'United States',
            'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Southwest_Airlines_logo_2014.svg/200px-Southwest_Airlines_logo_2014.svg.png',
            'website_url': 'https://www.southwest.com'
        },
        {
            'iata_code': 'AS',
            'icao_code': 'ASA',
            'name': 'Alaska Airlines',
            'callsign': 'Alaska',
            'country': 'United States',
            'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Alaska_Airlines_logo_2016.svg/200px-Alaska_Airlines_logo_2016.svg.png',
            'website_url': 'https://www.alaskaair.com'
        },
        {
            'iata_code': 'B6',
            'icao_code': 'JBU',
            'name': 'JetBlue Airways',
            'callsign': 'JetBlue',
            'country': 'United States',
            'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/JetBlue_logo.svg/200px-JetBlue_logo.svg.png',
            'website_url': 'https://www.jetblue.com'
        },
        {
            'iata_code': 'NK',
            'icao_code': 'NKS',
            'name': 'Spirit Airlines',
            'callsign': 'Spirit',
            'country': 'United States',
            'logo_url': 'https://upload.wikimedia.org/wikipedia/commons/thumb/9/9b/Spirit_Airlines_logo_2014.svg/200px-Spirit_Airlines_logo_2014.svg.png',
            'website_url': 'https://www.spirit.com'
        }
    ]
    
    with app.app_context():
        for airline_data in airlines_data:
            airline = Airline(**airline_data)
            db.session.add(airline)
        
        db.session.commit()
        print(f"✅ Added {len(airlines_data)} airlines")

def populate_aircraft():
    """Populate aircraft types"""
    print("Populating aircraft...")
    
    aircraft_data = [
        {
            'type_code': 'Boeing 737-800',
            'manufacturer': 'Boeing',
            'model': '737',
            'variant': '800',
            'capacity': 189,
            'range_km': 5765,
            'cruise_speed_kmh': 842
        },
        {
            'type_code': 'Boeing 737-900',
            'manufacturer': 'Boeing',
            'model': '737',
            'variant': '900',
            'capacity': 215,
            'range_km': 5926,
            'cruise_speed_kmh': 842
        },
        {
            'type_code': 'Airbus A320',
            'manufacturer': 'Airbus',
            'model': 'A320',
            'variant': '200',
            'capacity': 180,
            'range_km': 6150,
            'cruise_speed_kmh': 840
        },
        {
            'type_code': 'Boeing 777-200',
            'manufacturer': 'Boeing',
            'model': '777',
            'variant': '200',
            'capacity': 440,
            'range_km': 14320,
            'cruise_speed_kmh': 905
        },
        {
            'type_code': 'Boeing 757-200',
            'manufacturer': 'Boeing',
            'model': '757',
            'variant': '200',
            'capacity': 239,
            'range_km': 7222,
            'cruise_speed_kmh': 850
        },
        {
            'type_code': 'Airbus A321',
            'manufacturer': 'Airbus',
            'model': 'A321',
            'variant': '200',
            'capacity': 244,
            'range_km': 7400,
            'cruise_speed_kmh': 840
        },
        {
            'type_code': 'Boeing 787-8',
            'manufacturer': 'Boeing',
            'model': '787',
            'variant': '8',
            'capacity': 248,
            'range_km': 15200,
            'cruise_speed_kmh': 903
        },
        {
            'type_code': 'Airbus A330-200',
            'manufacturer': 'Airbus',
            'model': 'A330',
            'variant': '200',
            'capacity': 406,
            'range_km': 13400,
            'cruise_speed_kmh': 871
        },
        {
            'type_code': 'Boeing 737-MAX8',
            'manufacturer': 'Boeing',
            'model': '737 MAX',
            'variant': '8',
            'capacity': 189,
            'range_km': 6570,
            'cruise_speed_kmh': 842
        },
        {
            'type_code': 'Airbus A350-900',
            'manufacturer': 'Airbus',
            'model': 'A350',
            'variant': '900',
            'capacity': 315,
            'range_km': 15000,
            'cruise_speed_kmh': 903
        }
    ]
    
    with app.app_context():
        for aircraft_data_item in aircraft_data:
            aircraft = Aircraft(**aircraft_data_item)
            db.session.add(aircraft)
        
        db.session.commit()
        print(f"✅ Added {len(aircraft_data)} aircraft types")

def migrate_csv_data():
    """Migrate data from CSV to database"""
    print("Migrating CSV data to database...")
    
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'flights_lax_ord.csv')
        df = pd.read_csv(csv_path)
        
        with app.app_context():
            # Get reference data
            airports = {airport.iata_code: airport.id for airport in Airport.query.all()}
            airlines = {airline.name: airline.id for airline in Airline.query.all()}
            aircraft = {ac.type_code: ac.id for ac in Aircraft.query.all()}
            
            flights_added = 0
            
            for _, row in df.iterrows():
                # Parse flight data
                flight_number = row['flight_number']
                airline_name = row['airline']
                aircraft_type = row['aircraft_type']
                origin = row['origin']
                destination = row['destination']
                
                # Get IDs
                airline_id = airlines.get(airline_name)
                aircraft_id = aircraft.get(aircraft_type)
                origin_airport_id = airports.get(origin)
                destination_airport_id = airports.get(destination)
                
                if not all([airline_id, aircraft_id, origin_airport_id, destination_airport_id]):
                    print(f"⚠️  Skipping flight {flight_number} - missing reference data")
                    continue
                
                # Parse dates
                scheduled_departure = pd.to_datetime(row['scheduled_departure'])
                actual_departure = pd.to_datetime(row['actual_departure'])
                scheduled_arrival = pd.to_datetime(row['scheduled_arrival'])
                actual_arrival = pd.to_datetime(row['actual_arrival'])
                
                # Calculate flight date and duration
                flight_date = scheduled_departure.date()
                duration_minutes = int((scheduled_arrival - scheduled_departure).total_seconds() / 60)
                
                # Create flight record
                flight = Flight(
                    flight_number=flight_number,
                    airline_id=airline_id,
                    aircraft_id=aircraft_id,
                    origin_airport_id=origin_airport_id,
                    destination_airport_id=destination_airport_id,
                    scheduled_departure=scheduled_departure,
                    actual_departure=actual_departure,
                    scheduled_arrival=scheduled_arrival,
                    actual_arrival=actual_arrival,
                    gate=row['gate'],
                    status=row['status'],
                    delay_minutes=int(row['delay_minutes']),
                    seats_available=int(row['seats_available']) if pd.notna(row['seats_available']) else None,
                    on_time_probability=float(row['on_time_probability']) if pd.notna(row['on_time_probability']) else None,
                    flight_date=flight_date,
                    duration_minutes=duration_minutes,
                    distance_miles=1745,  # LAX-ORD distance
                    route_frequency='DAILY'
                )
                
                db.session.add(flight)
                flights_added += 1
            
            db.session.commit()
            print(f"✅ Migrated {flights_added} flights from CSV")
            
    except FileNotFoundError:
        print("⚠️  CSV file not found - skipping migration")
    except Exception as e:
        print(f"❌ Error migrating CSV data: {e}")

def populate_routes():
    """Populate route statistics"""
    print("Populating routes...")
    
    with app.app_context():
        # Get LAX and ORD airports
        lax = Airport.query.filter_by(iata_code='LAX').first()
        ord_airport = Airport.query.filter_by(iata_code='ORD').first()
        
        if lax and ord_airport:
            # Calculate route statistics from existing flights
            flights = Flight.query.filter_by(
                origin_airport_id=lax.id,
                destination_airport_id=ord_airport.id
            ).all()
            
            if flights:
                # Calculate statistics
                on_time_flights = [f for f in flights if f.status == 'ON_TIME']
                on_time_percentage = len(on_time_flights) / len(flights) * 100
                average_delay = sum(f.delay_minutes for f in flights) / len(flights)
                average_duration = sum(f.duration_minutes for f in flights if f.duration_minutes) / len([f for f in flights if f.duration_minutes])
                
                route = Route(
                    origin_airport_id=lax.id,
                    destination_airport_id=ord_airport.id,
                    average_duration_minutes=int(average_duration) if average_duration else 255,  # 4h 15m
                    distance_miles=1745,
                    on_time_percentage=on_time_percentage,
                    average_delay_minutes=average_delay,
                    flight_frequency='DAILY',
                    typical_aircraft_types='["B737-800", "B737-900", "A320", "B777-200"]'
                )
                
                db.session.add(route)
                db.session.commit()
                print("✅ Added LAX-ORD route statistics")

def main():
    """Main initialization function"""
    global app
    app = create_app()
    
    print("🚀 Initializing OnTime Database...")
    print("=" * 50)
    
    # Initialize database
    init_database()
    
    # Populate reference data
    populate_airports()
    populate_airlines()
    populate_aircraft()
    
    # Migrate existing CSV data
    migrate_csv_data()
    
    # Populate routes
    populate_routes()
    
    print("=" * 50)
    print("✅ Database initialization complete!")
    print(f"📁 Database file: {os.path.abspath('ontime.db')}")
    
    # Display summary
    with app.app_context():
        print(f"📊 Database Summary:")
        print(f"   Airports: {Airport.query.count()}")
        print(f"   Airlines: {Airline.query.count()}")
        print(f"   Aircraft: {Aircraft.query.count()}")
        print(f"   Flights: {Flight.query.count()}")
        print(f"   Routes: {Route.query.count()}")

if __name__ == '__main__':
    main()
