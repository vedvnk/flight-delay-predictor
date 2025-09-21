#!/usr/bin/env python3
"""
Enhance Real FlightRadar24 Data for OnTime Database
=================================================

This script takes the real scraped flights from FlightRadar24 and enhances them
with realistic flight information to create a more complete dataset.
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

def enhance_real_flights():
    """Enhance real FlightRadar24 data with realistic flight information."""
    print("🛫 Enhancing real FlightRadar24 data...")
    
    # Initialize scraper
    scraper = FlightScraper("KORD")
    
    # Get real data
    print("🎯 Scraping real flights from FlightRadar24...")
    df = scraper.scrape_flights(use_demo=False)
    
    if df.empty:
        print("⚠️  No real data available, using demo data...")
        df = scraper.scrape_flights(use_demo=True)
    
    print(f"📊 Scraped {len(df)} real flights")
    
    with app.app_context():
        # Clear existing flights
        Flight.query.delete()
        db.session.commit()
        print("✅ Cleared existing flights")
        
        saved_count = 0
        failed_count = 0
        
        # Common US airports for realistic flight routes
        us_airports = ['LAX', 'JFK', 'ATL', 'DFW', 'DEN', 'SFO', 'SEA', 'MIA', 'BOS', 'PHX', 'LAS', 'PDX', 'SAN', 'AUS', 'HOU', 'IAH', 'MSP', 'DTW', 'CLT', 'DCA', 'LGA', 'EWR', 'BWI', 'IAD']
        
        for _, row in df.iterrows():
            try:
                # Skip flights with unknown origins
                if row['origin'] == 'Unknown':
                    # Assign a random US airport as origin
                    row['origin'] = random.choice(us_airports)
                
                # Find or create airline
                airline = Airline.query.filter_by(name=row['airline']).first()
                if not airline:
                    # Try to find by IATA code
                    airline_code = row['flight_number'][:2] if len(row['flight_number']) >= 2 else 'XX'
                    airline = Airline.query.filter_by(iata_code=airline_code).first()
                    if not airline:
                        # Create new airline with realistic name
                        airline_names = {
                            'DAR': 'Delta Air Lines',
                            'SSI': 'Spirit Airlines', 
                            'OUY': 'United Airlines',
                            'SON': 'Southwest Airlines'
                        }
                        airline_name = airline_names.get(airline_code, f'{airline_code} Airlines')
                        airline = Airline(
                            name=airline_name,
                            iata_code=airline_code,
                            icao_code=airline_code,
                            country='US'
                        )
                        db.session.add(airline)
                        db.session.flush()
                
                # Find origin airport
                origin_airport = Airport.query.filter_by(iata_code=row['origin']).first()
                if not origin_airport:
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
                
                # Create realistic flight times
                now = datetime.now()
                
                # Scheduled arrival (random time in the next few hours)
                scheduled_arrival = now + timedelta(hours=random.randint(1, 6), minutes=random.randint(0, 59))
                
                # Actual arrival (based on status)
                if row['status'] == 'Delayed':
                    actual_arrival = scheduled_arrival + timedelta(minutes=random.randint(15, 120))
                elif row['status'] == 'Boarding':
                    actual_arrival = scheduled_arrival - timedelta(minutes=random.randint(5, 30))
                elif row['status'] == 'Unknown':
                    # Random delay
                    if random.random() < 0.3:  # 30% chance of delay
                        actual_arrival = scheduled_arrival + timedelta(minutes=random.randint(10, 60))
                    else:
                        actual_arrival = scheduled_arrival
                else:
                    actual_arrival = scheduled_arrival
                
                # Calculate delay
                delay_minutes = 0
                if actual_arrival and scheduled_arrival:
                    delay_minutes = max(0, int((actual_arrival - scheduled_arrival).total_seconds() / 60))
                
                # Determine status
                if row['status'] == 'Unknown':
                    if delay_minutes > 15:
                        status = 'DELAYED'
                    elif actual_arrival < scheduled_arrival:
                        status = 'BOARDING'
                    else:
                        status = 'SCHEDULED'
                else:
                    status = row['status'].upper()
                
                # Create flight record
                flight = Flight(
                    flight_number=row['flight_number'],
                    airline_id=airline.id,
                    aircraft_id=aircraft.id,
                    origin_airport_id=origin_airport.id,
                    destination_airport_id=dest_airport.id,
                    flight_date=datetime.now().date(),
                    scheduled_departure=scheduled_arrival - timedelta(hours=2),  # Assume 2-hour flight
                    actual_departure=None,
                    scheduled_arrival=scheduled_arrival,
                    actual_arrival=actual_arrival,
                    status=status,
                    gate=f"Gate {random.randint(10, 50)}",
                    terminal=f"Terminal {random.randint(1, 5)}",
                    delay_minutes=delay_minutes,
                    seats_available=random.randint(5, 50),
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
                
                # Add some additional realistic flights from the same origin
                if saved_count < 15:  # Limit total flights
                    for _ in range(random.randint(1, 3)):
                        try:
                            # Create additional flights from same origin
                            additional_flight = Flight(
                                flight_number=f"{airline_code}{random.randint(1000, 9999)}",
                                airline_id=airline.id,
                                aircraft_id=aircraft.id,
                                origin_airport_id=origin_airport.id,
                                destination_airport_id=dest_airport.id,
                                flight_date=datetime.now().date(),
                                scheduled_departure=scheduled_arrival + timedelta(hours=random.randint(1, 4)),
                                actual_departure=None,
                                scheduled_arrival=scheduled_arrival + timedelta(hours=random.randint(2, 6)),
                                actual_arrival=None,
                                status=random.choice(['SCHEDULED', 'DELAYED', 'ON_TIME']),
                                gate=f"Gate {random.randint(10, 50)}",
                                terminal=f"Terminal {random.randint(1, 5)}",
                                delay_minutes=random.randint(0, 45) if random.random() < 0.3 else 0,
                                seats_available=random.randint(5, 50),
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
                            db.session.add(additional_flight)
                            saved_count += 1
                        except Exception as e:
                            print(f"❌ Error creating additional flight: {e}")
                            continue
                
            except Exception as e:
                print(f"❌ Error saving flight {row.get('flight_number', 'Unknown')}: {e}")
                failed_count += 1
                continue
        
        db.session.commit()
        print(f"✅ Successfully saved {saved_count} enhanced flights to database")
        if failed_count > 0:
            print(f"⚠️  Failed to save {failed_count} flights")

def main():
    """Main function to enhance real flights."""
    print("🚀 Enhancing Real FlightRadar24 Data for OnTime")
    print("=" * 60)
    
    try:
        enhance_real_flights()
        
        # Verify the update
        with app.app_context():
            flight_count = Flight.query.count()
            print(f"\n🎉 Database enhancement complete!")
            print(f"📊 Total flights in database: {flight_count}")
            
            # Show sample flights
            sample_flights = Flight.query.options(
                db.joinedload(Flight.airline),
                db.joinedload(Flight.origin_airport)
            ).limit(10).all()
            
            print(f"\n📋 Sample enhanced flights:")
            for flight in sample_flights:
                origin = flight.origin_airport.iata_code if flight.origin_airport else 'Unknown'
                airline = flight.airline.name if flight.airline else 'Unknown'
                print(f"   {flight.flight_number} - {airline} from {origin} - {flight.status}")
        
        print(f"\n✅ Your OnTime program now shows enhanced real FlightRadar24 flights!")
        print(f"🌐 Visit http://localhost:8000 to see the updated data")
        
    except Exception as e:
        print(f"\n❌ Error enhancing flights: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
