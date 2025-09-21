#!/usr/bin/env python3
"""
Update OnTime Database with Real-time Scraped Flight Data
=========================================================

This script scrapes real-time flight data and replaces the existing database
so the OnTime program shows live flight information.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from final_flight_scraper import FlightScraper
from app import app
from models import db, Flight, Airport, Airline, Aircraft

def clear_existing_flights():
    """Clear all existing flights from the database."""
    print("🗑️  Clearing existing flight data...")
    
    with app.app_context():
        try:
            # Delete all existing flights
            Flight.query.delete()
            db.session.commit()
            print("✅ Cleared existing flights")
        except Exception as e:
            print(f"❌ Error clearing flights: {e}")
            db.session.rollback()

def create_missing_airports():
    """Ensure all required airports exist in the database."""
    print("🏢 Creating missing airports...")
    
    with app.app_context():
        # Common airports that might appear in scraped data
        airports_data = [
            {'iata_code': 'ORD', 'icao_code': 'KORD', 'name': 'Chicago O\'Hare International Airport', 'city': 'Chicago', 'state': 'IL', 'country': 'US'},
            {'iata_code': 'LAX', 'icao_code': 'KLAX', 'name': 'Los Angeles International Airport', 'city': 'Los Angeles', 'state': 'CA', 'country': 'US'},
            {'iata_code': 'JFK', 'icao_code': 'KJFK', 'name': 'John F. Kennedy International Airport', 'city': 'New York', 'state': 'NY', 'country': 'US'},
            {'iata_code': 'ATL', 'icao_code': 'KATL', 'name': 'Hartsfield-Jackson Atlanta International Airport', 'city': 'Atlanta', 'state': 'GA', 'country': 'US'},
            {'iata_code': 'DFW', 'icao_code': 'KDFW', 'name': 'Dallas/Fort Worth International Airport', 'city': 'Dallas', 'state': 'TX', 'country': 'US'},
            {'iata_code': 'DEN', 'icao_code': 'KDEN', 'name': 'Denver International Airport', 'city': 'Denver', 'state': 'CO', 'country': 'US'},
            {'iata_code': 'SFO', 'icao_code': 'KSFO', 'name': 'San Francisco International Airport', 'city': 'San Francisco', 'state': 'CA', 'country': 'US'},
            {'iata_code': 'SEA', 'icao_code': 'KSEA', 'name': 'Seattle-Tacoma International Airport', 'city': 'Seattle', 'state': 'WA', 'country': 'US'},
            {'iata_code': 'MIA', 'icao_code': 'KMIA', 'name': 'Miami International Airport', 'city': 'Miami', 'state': 'FL', 'country': 'US'},
            {'iata_code': 'BOS', 'icao_code': 'KBOS', 'name': 'Logan International Airport', 'city': 'Boston', 'state': 'MA', 'country': 'US'},
            {'iata_code': 'PHX', 'icao_code': 'KPHX', 'name': 'Phoenix Sky Harbor International Airport', 'city': 'Phoenix', 'state': 'AZ', 'country': 'US'},
            {'iata_code': 'LAS', 'icao_code': 'KLAS', 'name': 'Harry Reid International Airport', 'city': 'Las Vegas', 'state': 'NV', 'country': 'US'},
            {'iata_code': 'PDX', 'icao_code': 'KPDX', 'name': 'Portland International Airport', 'city': 'Portland', 'state': 'OR', 'country': 'US'},
            {'iata_code': 'SAN', 'icao_code': 'KSAN', 'name': 'San Diego International Airport', 'city': 'San Diego', 'state': 'CA', 'country': 'US'},
            {'iata_code': 'AUS', 'icao_code': 'KAUS', 'name': 'Austin-Bergstrom International Airport', 'city': 'Austin', 'state': 'TX', 'country': 'US'},
            {'iata_code': 'HOU', 'icao_code': 'KHOU', 'name': 'William P. Hobby Airport', 'city': 'Houston', 'state': 'TX', 'country': 'US'},
            {'iata_code': 'IAH', 'icao_code': 'KIAH', 'name': 'George Bush Intercontinental Airport', 'city': 'Houston', 'state': 'TX', 'country': 'US'},
            {'iata_code': 'MSP', 'icao_code': 'KMSP', 'name': 'Minneapolis-Saint Paul International Airport', 'city': 'Minneapolis', 'state': 'MN', 'country': 'US'},
            {'iata_code': 'DTW', 'icao_code': 'KDTW', 'name': 'Detroit Metropolitan Wayne County Airport', 'city': 'Detroit', 'state': 'MI', 'country': 'US'},
            {'iata_code': 'CLT', 'icao_code': 'KCLT', 'name': 'Charlotte Douglas International Airport', 'city': 'Charlotte', 'state': 'NC', 'country': 'US'},
            {'iata_code': 'DCA', 'icao_code': 'KDCA', 'name': 'Ronald Reagan Washington National Airport', 'city': 'Washington', 'state': 'DC', 'country': 'US'},
            {'iata_code': 'LGA', 'icao_code': 'KLGA', 'name': 'LaGuardia Airport', 'city': 'New York', 'state': 'NY', 'country': 'US'},
            {'iata_code': 'EWR', 'icao_code': 'KEWR', 'name': 'Newark Liberty International Airport', 'city': 'Newark', 'state': 'NJ', 'country': 'US'},
            {'iata_code': 'BWI', 'icao_code': 'KBWI', 'name': 'Baltimore/Washington International Thurgood Marshall Airport', 'city': 'Baltimore', 'state': 'MD', 'country': 'US'},
            {'iata_code': 'IAD', 'icao_code': 'KIAD', 'name': 'Washington Dulles International Airport', 'city': 'Washington', 'state': 'DC', 'country': 'US'},
        ]
        
        created_count = 0
        for airport_data in airports_data:
            existing = Airport.query.filter_by(iata_code=airport_data['iata_code']).first()
            if not existing:
                airport = Airport(**airport_data)
                db.session.add(airport)
                created_count += 1
        
        db.session.commit()
        print(f"✅ Created {created_count} missing airports")

def create_missing_airlines():
    """Ensure all required airlines exist in the database."""
    print("✈️  Creating missing airlines...")
    
    with app.app_context():
        airlines_data = [
            {'name': 'American Airlines', 'iata_code': 'AA', 'icao_code': 'AAL', 'country': 'US'},
            {'name': 'United Airlines', 'iata_code': 'UA', 'icao_code': 'UAL', 'country': 'US'},
            {'name': 'Delta Air Lines', 'iata_code': 'DL', 'icao_code': 'DAL', 'country': 'US'},
            {'name': 'Southwest Airlines', 'iata_code': 'WN', 'icao_code': 'SWA', 'country': 'US'},
            {'name': 'Alaska Airlines', 'iata_code': 'AS', 'icao_code': 'ASA', 'country': 'US'},
            {'name': 'JetBlue Airways', 'iata_code': 'B6', 'icao_code': 'JBU', 'country': 'US'},
            {'name': 'Frontier Airlines', 'iata_code': 'F9', 'icao_code': 'FFT', 'country': 'US'},
            {'name': 'Spirit Airlines', 'iata_code': 'NK', 'icao_code': 'NKS', 'country': 'US'},
            {'name': 'Allegiant Air', 'iata_code': 'G4', 'icao_code': 'AAY', 'country': 'US'},
            {'name': 'Sun Country Airlines', 'iata_code': 'SY', 'icao_code': 'SCX', 'country': 'US'},
            {'name': 'Republic Airways', 'iata_code': 'YX', 'icao_code': 'RPA', 'country': 'US'},
            {'name': 'American Eagle', 'iata_code': 'MQ', 'icao_code': 'ENY', 'country': 'US'},
            {'name': 'SkyWest Airlines', 'iata_code': 'OO', 'icao_code': 'SKW', 'country': 'US'},
            {'name': 'ExpressJet', 'iata_code': 'EV', 'icao_code': 'ASQ', 'country': 'US'},
            {'name': 'Endeavor Air', 'iata_code': '9E', 'icao_code': 'EDV', 'country': 'US'},
            {'name': 'Mesa Airlines', 'iata_code': 'YV', 'icao_code': 'ASH', 'country': 'US'},
            {'name': 'PSA Airlines', 'iata_code': 'OH', 'icao_code': 'JIA', 'country': 'US'},
        ]
        
        created_count = 0
        for airline_data in airlines_data:
            existing = Airline.query.filter_by(name=airline_data['name']).first()
            if not existing:
                airline = Airline(**airline_data)
                db.session.add(airline)
                created_count += 1
        
        db.session.commit()
        print(f"✅ Created {created_count} missing airlines")

def create_missing_aircraft():
    """Ensure common aircraft types exist in the database."""
    print("🛩️  Creating missing aircraft...")
    
    with app.app_context():
        aircraft_data = [
            {'type_code': 'Boeing 737-800', 'manufacturer': 'Boeing', 'model': '737', 'variant': '800', 'capacity': 189, 'range_km': 5765, 'cruise_speed_kmh': 842},
            {'type_code': 'Boeing 737-900', 'manufacturer': 'Boeing', 'model': '737', 'variant': '900', 'capacity': 215, 'range_km': 5926, 'cruise_speed_kmh': 842},
            {'type_code': 'Airbus A320', 'manufacturer': 'Airbus', 'model': 'A320', 'variant': '200', 'capacity': 180, 'range_km': 6150, 'cruise_speed_kmh': 840},
            {'type_code': 'Boeing 777-200', 'manufacturer': 'Boeing', 'model': '777', 'variant': '200', 'capacity': 440, 'range_km': 9700, 'cruise_speed_kmh': 905},
            {'type_code': 'Boeing 757-200', 'manufacturer': 'Boeing', 'model': '757', 'variant': '200', 'capacity': 200, 'range_km': 7222, 'cruise_speed_kmh': 850},
            {'type_code': 'Airbus A321', 'manufacturer': 'Airbus', 'model': 'A321', 'variant': '200', 'capacity': 220, 'range_km': 5950, 'cruise_speed_kmh': 840},
            {'type_code': 'Boeing 787-8', 'manufacturer': 'Boeing', 'model': '787', 'variant': '8', 'capacity': 242, 'range_km': 13620, 'cruise_speed_kmh': 913},
            {'type_code': 'Airbus A330-300', 'manufacturer': 'Airbus', 'model': 'A330', 'variant': '300', 'capacity': 440, 'range_km': 11750, 'cruise_speed_kmh': 871},
        ]
        
        created_count = 0
        for aircraft_data_item in aircraft_data:
            existing = Aircraft.query.filter_by(type_code=aircraft_data_item['type_code']).first()
            if not existing:
                aircraft = Aircraft(**aircraft_data_item)
                db.session.add(aircraft)
                created_count += 1
        
        db.session.commit()
        print(f"✅ Created {created_count} missing aircraft")

def scrape_and_save_flights():
    """Scrape real-time flights and save to database."""
    print("🛫 Scraping real-time flight data...")
    
    # Initialize scraper
    scraper = FlightScraper("KORD")
    
    # Try to scrape real data, fall back to demo data if needed
    df = scraper.scrape_flights(use_demo=False)
    
    if df.empty:
        print("⚠️  No real data available, using demo data...")
        df = scraper.scrape_flights(use_demo=True)
    
    print(f"📊 Scraped {len(df)} flights")
    
    with app.app_context():
        saved_count = 0
        failed_count = 0
        
        for _, row in df.iterrows():
            try:
                # Find or create airline
                airline = Airline.query.filter_by(name=row['airline']).first()
                if not airline:
                    # Try to find by IATA code
                    airline_code = row['flight_number'][:2] if len(row['flight_number']) >= 2 else 'XX'
                    airline = Airline.query.filter_by(iata_code=airline_code).first()
                    if not airline:
                        # Create new airline
                        airline = Airline(
                            name=row['airline'],
                            iata_code=airline_code,
                            icao_code=airline_code,
                            country='US'
                        )
                        db.session.add(airline)
                        db.session.flush()
                
                # Find origin airport
                origin_airport = Airport.query.filter_by(iata_code=row['origin']).first()
                if not origin_airport:
                    # Skip flights with unknown origins
                    print(f"⚠️  Skipping flight {row['flight_number']} - unknown origin: {row['origin']}")
                    failed_count += 1
                    continue
                
                # Find destination airport (ORD)
                dest_airport = Airport.query.filter_by(iata_code='ORD').first()
                if not dest_airport:
                    print("❌ ORD airport not found in database!")
                    failed_count += 1
                    continue
                
                # Get a random aircraft type
                aircraft = Aircraft.query.first()
                if not aircraft:
                    # Create a default aircraft if none exist
                    aircraft = Aircraft(
                        type_code='Boeing 737-800',
                        manufacturer='Boeing',
                        model='737',
                        variant='800',
                        capacity=189,
                        range_km=5765,
                        cruise_speed_kmh=842
                    )
                    db.session.add(aircraft)
                    db.session.flush()
                
                # Parse times
                try:
                    if row['scheduled_arrival'] != 'Unknown':
                        scheduled_time = datetime.strptime(row['scheduled_arrival'], '%H:%M')
                        scheduled_time = scheduled_time.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
                    else:
                        scheduled_time = datetime.now()
                except:
                    scheduled_time = datetime.now()
                
                try:
                    if row['actual_arrival'] != 'Unknown':
                        actual_time = datetime.strptime(row['actual_arrival'], '%H:%M')
                        actual_time = actual_time.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
                    else:
                        actual_time = None
                except:
                    actual_time = None
                
                # Calculate delay
                delay_minutes = 0
                if actual_time and scheduled_time:
                    delay_minutes = max(0, int((actual_time - scheduled_time).total_seconds() / 60))
                
                # Determine status
                status = row['status'].upper() if row['status'] != 'Unknown' else 'SCHEDULED'
                
                # Create flight record
                flight = Flight(
                    flight_number=row['flight_number'],
                    airline_id=airline.id,
                    aircraft_id=aircraft.id,
                    origin_airport_id=origin_airport.id,
                    destination_airport_id=dest_airport.id,
                    flight_date=datetime.now().date(),
                    scheduled_departure=scheduled_time - timedelta(hours=2),  # Assume 2-hour flight
                    actual_departure=None,
                    scheduled_arrival=scheduled_time,
                    actual_arrival=actual_time,
                    status=status,
                    gate=row.get('gate', 'TBD'),
                    terminal=row.get('terminal', 'TBD'),
                    delay_minutes=delay_minutes,
                    seats_available=random.randint(10, 50),
                    total_seats=aircraft.capacity,
                    load_factor=random.uniform(0.7, 0.95),
                    on_time_probability=random.uniform(0.6, 0.9),
                    delay_probability=random.uniform(0.1, 0.4),
                    cancellation_probability=random.uniform(0.01, 0.05),
                    base_price=random.uniform(200, 800),
                    current_price=random.uniform(200, 800),
                    currency='USD',
                    duration_minutes=random.randint(120, 360),
                    distance_miles=random.randint(500, 2500)
                )
                
                db.session.add(flight)
                saved_count += 1
                
            except Exception as e:
                print(f"❌ Error saving flight {row.get('flight_number', 'Unknown')}: {e}")
                failed_count += 1
                continue
        
        db.session.commit()
        print(f"✅ Successfully saved {saved_count} flights to database")
        if failed_count > 0:
            print(f"⚠️  Failed to save {failed_count} flights")

def main():
    """Main function to update database with scraped flights."""
    print("🚀 OnTime Database Update with Real-time Flight Data")
    print("=" * 60)
    
    try:
        # Step 1: Clear existing flights
        clear_existing_flights()
        
        # Step 2: Ensure all required data exists
        create_missing_airports()
        create_missing_airlines()
        create_missing_aircraft()
        
        # Step 3: Scrape and save new flights
        scrape_and_save_flights()
        
        # Step 4: Verify the update
        with app.app_context():
            flight_count = Flight.query.count()
            print(f"\n🎉 Database update complete!")
            print(f"📊 Total flights in database: {flight_count}")
            
            # Show sample flights
            sample_flights = Flight.query.options(
                db.joinedload(Flight.airline),
                db.joinedload(Flight.origin_airport)
            ).limit(5).all()
            
            print(f"\n📋 Sample flights:")
            for flight in sample_flights:
                origin = flight.origin_airport.iata_code if flight.origin_airport else 'Unknown'
                airline = flight.airline.name if flight.airline else 'Unknown'
                print(f"   {flight.flight_number} - {airline} from {origin} - {flight.status}")
        
        print(f"\n✅ Your OnTime program will now show the latest scraped flights!")
        print(f"🌐 Visit http://localhost:8000 to see the updated data")
        
    except Exception as e:
        print(f"\n❌ Error updating database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
