#!/usr/bin/env python3
"""
Load More Flights
================

This script loads thousands of realistic flights across all airports
for the next couple of months.
"""

import sys
import os
from datetime import datetime, timedelta, date
import random
from typing import Dict, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from app import app
from models import db, Flight, Airport, Airline, Aircraft
from delay_reason_analyzer import DelayReasonAnalyzer, DelayReason

def load_more_flights():
    """Load thousands of realistic flights across all airports"""
    print("🛫 Loading thousands of realistic flights...")
    
    with app.app_context():
        # Get all airports, airlines, and aircraft
        airports = Airport.query.all()
        airlines = Airline.query.all()
        aircraft = Aircraft.query.all()
        
        if not airports or not airlines or not aircraft:
            print("❌ Missing required data. Please run init_db.py first.")
            return 0
        
        print(f"📍 Found {len(airports)} airports")
        print(f"✈️  Found {len(airlines)} airlines")
        print(f"🛩️  Found {len(aircraft)} aircraft types")
        
        delay_analyzer = DelayReasonAnalyzer()
        total_flights_generated = 0
        
        # Generate flights for the next 60 days
        base_date = date.today()
        
        for day_offset in range(60):  # Next 60 days
            flight_date = base_date + timedelta(days=day_offset)
            print(f"📅 Generating flights for {flight_date}")
            
            flights_this_day = 0
            
            # Generate flights between random airport pairs
            for _ in range(1000):  # 1000 flights per day
                # Select random airports
                origin_airport = random.choice(airports)
                destination_airport = random.choice(airports)
                
                # Skip if same airport
                if origin_airport.id == destination_airport.id:
                    continue
                
                # Select random airline and aircraft
                airline = random.choice(airlines)
                aircraft_obj = random.choice(aircraft)
                
                # Generate realistic flight times
                hour = random.randint(5, 23)
                minute = random.choice([0, 15, 30, 45])
                scheduled_departure = datetime.combine(
                    flight_date, 
                    datetime.min.time().replace(hour=hour, minute=minute)
                )
                
                # Calculate flight duration (1-12 hours)
                duration_minutes = random.randint(60, 720)
                scheduled_arrival = scheduled_departure + timedelta(minutes=duration_minutes)
                
                # Generate realistic delays
                delay_breakdown = {
                    'weather': random.randint(0, 30) if random.random() < 0.15 else 0,
                    'air_traffic': random.randint(0, 25) if random.random() < 0.20 else 0,
                    'security': random.randint(0, 15) if random.random() < 0.10 else 0,
                    'mechanical': random.randint(0, 60) if random.random() < 0.05 else 0,
                    'crew': random.randint(0, 20) if random.random() < 0.08 else 0
                }
                
                total_delay = sum(delay_breakdown.values())
                
                # Determine status
                if total_delay > 60:
                    status = 'CANCELLED'
                elif total_delay > 15:
                    status = 'DELAYED'
                else:
                    status = 'ON_TIME'
                
                # Calculate delay percentage
                delay_percentage = (total_delay / duration_minutes) * 100 if duration_minutes > 0 else 0
                
                # Generate flight number
                flight_number = f"{airline.iata_code or 'XX'}{random.randint(100, 9999)}"
                
                # Create flight data for delay analysis
                flight_data = {
                    'delay_minutes': total_delay,
                    'weather_delay_minutes': delay_breakdown['weather'],
                    'air_traffic_delay_minutes': delay_breakdown['air_traffic'],
                    'security_delay_minutes': delay_breakdown['security'],
                    'mechanical_delay_minutes': delay_breakdown['mechanical'],
                    'crew_delay_minutes': delay_breakdown['crew'],
                    'current_weather_delay_risk': random.uniform(0.1, 0.3),
                    'current_air_traffic_delay_risk': random.uniform(0.1, 0.4),
                    'scheduled_departure': scheduled_departure
                }
                
                # Analyze delay reasons
                analysis = delay_analyzer.analyze_delay_reasons(flight_data)
                
                # Create flight
                flight = Flight(
                    flight_number=flight_number,
                    airline_id=airline.id,
                    aircraft_id=aircraft_obj.id,
                    origin_airport_id=origin_airport.id,
                    destination_airport_id=destination_airport.id,
                    scheduled_departure=scheduled_departure,
                    actual_departure=scheduled_departure + timedelta(minutes=total_delay) if status != 'CANCELLED' else None,
                    scheduled_arrival=scheduled_arrival,
                    actual_arrival=scheduled_arrival + timedelta(minutes=total_delay) if status != 'CANCELLED' else None,
                    gate=f"{random.choice(['A', 'B', 'CGT', 'D', 'E'])}{random.randint(1, 50)}",
                    terminal=f"T{random.randint(1, 5)}",
                    status=status,
                    delay_minutes=total_delay if status != 'CANCELLED' else 0,
                    delay_percentage=delay_percentage,
                    seats_available=random.randint(0, aircraft_obj.capacity),
                    total_seats=aircraft_obj.capacity,
                    load_factor=random.uniform(0.6, 0.95),
                    on_time_probability=random.uniform(0.7, 0.9),
                    delay_probability=random.uniform(0.1, 0.3),
                    cancellation_probability=0.02,
                    base_price=random.uniform(200, 1200),
                    current_price=random.uniform(200, 1200),
                    flight_date=flight_date,
                    duration_minutes=duration_minutes,
                    distance_miles=random.randint(200, 8000),
                    route_frequency='DAILY',
                    
                    # Comprehensive delay metrics
                    weather_delay_minutes=delay_breakdown['weather'],
                    air_traffic_delay_minutes=delay_breakdown['air_traffic'],
                    security_delay_minutes=delay_breakdown['security'],
                    mechanical_delay_minutes=delay_breakdown['mechanical'],
                    crew_delay_minutes=delay_breakdown['crew'],
                    
                    # Historical performance
                    route_on_time_percentage=random.uniform(0.75, 0.90),
                    airline_on_time_percentage=random.uniform(0.75, 0.90),
                    time_of_day_delay_factor=random.uniform(0.9, 1.3),
                    day_of_week_delay_factor=random.uniform(0.9, 1.2),
                    seasonal_delay_factor=random.uniform(0.9, 1.2),
                    
                    # Current conditions
                    current_weather_delay_risk=flight_data['current_weather_delay_risk'],
                    current_air_traffic_delay_risk=flight_data['current_air_traffic_delay_risk'],
                    current_airport_congestion_level=random.uniform(0.3, 0.8),
                    
                    # Delay reason analysis
                    primary_delay_reason=analysis.primary_reason.value,
                    primary_delay_reason_percentage=analysis.primary_percentage,
                    secondary_delay_reason=analysis.secondary_reason.value if analysis.secondary_reason else None,
                    delay_reason_confidence=analysis.confidence
                )
                
                db.session.add(flight)
                flights_this_day += 1
                total_flights_generated += 1
            
            # Commit flights for this day
            db.session.commit()
            print(f"✅ Generated {flights_this_day} flights for {flight_date}")
        
        print(f"\n🎉 Generated {total_flights_generated} flights across 60 days!")
        
        # Show statistics
        total_flights = Flight.query.count()
        delayed_flights = Flight.query.filter(Flight.delay_minutes > 0).count()
        cancelled_flights = Flight.query.filter(Flight.status == 'CANCELLED').count()
        
        print(f"\n📊 Database Statistics:")
        print(f"   Total flights: {total_flights:,}")
        print(f"   Delayed flights: {delayed_flights:,}")
        print(f"   Cancelled flights: {cancelled_flights:,}")
        print(f"   On-time flights: {total_flights - delayed_flights - cancelled_flights:,}")
        
        return total_flights_generated

def main():
    """Main function to load more flights"""
    print("🛫 Load More Flights")
    print("=" * 50)
    
    try:
        flights_generated = load_more_flights()
        print(f"\n✅ Successfully loaded {flights_generated} flights!")
        print(f"🌐 Visit http://localhost:8000 to see the comprehensive flight data")
        
    except Exception as e:
        print(f"\n❌ Error loading flights: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
