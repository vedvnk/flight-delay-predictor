#!/usr/bin/env python3
"""
Extended Flight Generator
========================

This script generates flights for a wide range of dates to ensure
coverage beyond September 23rd, 2025.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from app import app
from models import db, Flight, Airport, Airline, Aircraft

def generate_flights_for_date_range():
    """Generate flights for a wide range of dates."""
    
    with app.app_context():
        # Clear existing flights
        Flight.query.delete()
        db.session.commit()
        print("✅ Cleared existing flights")
        
        # Get existing data
        ord_airport = Airport.query.filter_by(iata_code='ORD').first()
        airlines = Airline.query.all()
        aircraft_types = Aircraft.query.all()
        
        # Major US airports with realistic ORD routes
        major_airports = [
            'LAX', 'JFK', 'LGA', 'EWR', 'ATL', 'DFW', 'DEN', 'SFO', 'SEA', 
            'MIA', 'BOS', 'PHX', 'LAS', 'PDX', 'SAN', 'AUS', 'HOU', 'IAH', 
            'MSP', 'DTW', 'CLT', 'DCA', 'BWI', 'IAD', 'SLC', 'MCO', 'TPA',
            'FLL', 'RDU', 'BNA', 'STL', 'CLE', 'PIT', 'CVG', 'IND', 'MKE'
        ]
        
        origin_airports = Airport.query.filter(Airport.iata_code.in_(major_airports)).all()
        
        flights_created = 0
        
        # Generate flights for the next 60 days
        start_date = datetime.now().date()
        
        for day_offset in range(60):
            flight_date = start_date + timedelta(days=day_offset)
            
            print(f"📅 Generating flights for {flight_date}")
            
            # Generate 8-12 flights per day for major routes
            flights_per_day = random.randint(8, 12)
            
            for i in range(flights_per_day):
                try:
                    # Select random origin airport
                    origin_airport = random.choice(origin_airports)
                    airline = random.choice(airlines)
                    aircraft = random.choice(aircraft_types)
                    
                    # Generate realistic timing
                    departure_hour = random.randint(6, 22)
                    departure_minute = random.choice([0, 15, 30, 45])
                    
                    # Create departure time
                    departure_time = datetime.combine(
                        flight_date, 
                        datetime.min.time().replace(hour=departure_hour, minute=departure_minute)
                    )
                    
                    # Calculate arrival time (1-4 hours later)
                    duration_minutes = random.randint(60, 240)
                    arrival_time = departure_time + timedelta(minutes=duration_minutes)
                    
                    # Generate realistic flight number
                    airline_code = airline.iata_code or airline.name[:2].upper()
                    flight_number = f"{airline_code}{random.randint(1000, 9999)}"
                    
                    # Determine status and actual times
                    status_weights = {
                        'ON_TIME': 0.65,
                        'DELAYED': 0.25,
                        'SCHEDULED': 0.08,
                        'BOARDING': 0.02
                    }
                    
                    status = random.choices(
                        list(status_weights.keys()), 
                        weights=list(status_weights.values())
                    )[0]
                    
                    # Calculate actual times
                    delay_minutes = 0
                    actual_departure = None
                    actual_arrival = None
                    
                    if status == 'DELAYED':
                        delay_minutes = random.randint(15, 120)
                        actual_departure = departure_time + timedelta(minutes=delay_minutes)
                        actual_arrival = arrival_time + timedelta(minutes=delay_minutes)
                    elif status == 'BOARDING':
                        delay_minutes = random.randint(-10, 5)
                        actual_departure = departure_time + timedelta(minutes=delay_minutes)
                        actual_arrival = arrival_time + timedelta(minutes=delay_minutes)
                    elif status == 'ON_TIME':
                        # Small realistic variations
                        departure_variation = random.randint(-5, 5)
                        actual_departure = departure_time + timedelta(minutes=departure_variation)
                        actual_arrival = arrival_time + timedelta(minutes=departure_variation)
                    
                    # Calculate probabilities
                    on_time_prob = 0.8
                    delay_prob = 0.15
                    cancel_prob = 0.02
                    
                    # Adjust based on time of day
                    if departure_hour in [7, 8, 17, 18, 19]:
                        on_time_prob = 0.6
                        delay_prob = 0.35
                    
                    # Create flight record
                    flight = Flight(
                        flight_number=flight_number,
                        airline_id=airline.id,
                        aircraft_id=aircraft.id,
                        origin_airport_id=origin_airport.id,
                        destination_airport_id=ord_airport.id,
                        flight_date=flight_date,
                        scheduled_departure=departure_time,
                        actual_departure=actual_departure,
                        scheduled_arrival=arrival_time,
                        actual_arrival=actual_arrival,
                        status=status,
                        gate=f"Gate {random.randint(10, 50)}",
                        terminal=f"Terminal {random.randint(1, 5)}",
                        delay_minutes=delay_minutes,
                        seats_available=random.randint(5, aircraft.capacity // 2),
                        total_seats=aircraft.capacity,
                        load_factor=random.uniform(0.7, 0.95),
                        on_time_probability=on_time_prob,
                        delay_probability=delay_prob,
                        cancellation_probability=cancel_prob,
                        base_price=random.uniform(200, 800),
                        current_price=random.uniform(200, 800),
                        currency='USD',
                        duration_minutes=duration_minutes,
                        distance_miles=random.randint(500, 2500)
                    )
                    
                    db.session.add(flight)
                    flights_created += 1
                    
                except Exception as e:
                    print(f"❌ Error creating flight: {e}")
                    continue
        
        # Commit all flights
        db.session.commit()
        
        print(f"✅ Successfully created {flights_created} flights across 60 days")
        
        # Show statistics
        total_flights = Flight.query.count()
        print(f"\n📊 Database Statistics:")
        print(f"   Total flights: {total_flights}")
        
        # Show date range
        earliest = db.session.query(db.func.min(Flight.flight_date)).scalar()
        latest = db.session.query(db.func.max(Flight.flight_date)).scalar()
        print(f"   Date range: {earliest} to {latest}")
        
        # Show flights per date
        date_counts = db.session.query(
            Flight.flight_date,
            db.func.count(Flight.id).label('count')
        ).group_by(Flight.flight_date).order_by(Flight.flight_date).limit(10).all()
        
        print(f"\n📅 Sample flight dates:")
        for date_count in date_counts:
            print(f"   {date_count.flight_date}: {date_count.count} flights")
        
        return flights_created

def main():
    """Main function."""
    print("🚀 Extended Flight Generator")
    print("=" * 60)
    print("🎯 Generating flights for 60 days from today")
    print("=" * 60)
    
    flights_created = generate_flights_for_date_range()
    
    print(f"\n🎉 Extended Generation Complete!")
    print(f"📊 Total flights created: {flights_created}")
    print(f"🌐 Your OnTime program now has flights for dates beyond September 23rd!")

if __name__ == "__main__":
    main()
