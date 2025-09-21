#!/usr/bin/env python3
"""
Generate Comprehensive ORD Flight Data
=====================================

This script generates realistic flight data for Chicago O'Hare (ORD) based on
actual airport patterns and schedules. ORD is one of the world's busiest airports
and should have hundreds of flights per day.
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from app import app
from models import db, Flight, Airport, Airline, Aircraft

def generate_comprehensive_ord_flights():
    """Generate comprehensive realistic flight data for ORD."""
    print("🛫 Generating comprehensive ORD flight data...")
    
    with app.app_context():
        # Clear existing flights
        Flight.query.delete()
        db.session.commit()
        print("✅ Cleared existing flights")
        
        # Get ORD airport
        ord_airport = Airport.query.filter_by(iata_code='ORD').first()
        if not ord_airport:
            print("❌ ORD airport not found in database!")
            return
        
        # Get all airlines and aircraft
        airlines = Airline.query.all()
        aircraft_types = Aircraft.query.all()
        
        if not airlines or not aircraft_types:
            print("❌ No airlines or aircraft found in database!")
            return
        
        # Major US airports that commonly serve ORD
        major_airports = [
            'LAX', 'JFK', 'LGA', 'EWR', 'ATL', 'DFW', 'DEN', 'SFO', 'SEA', 
            'MIA', 'BOS', 'PHX', 'LAS', 'PDX', 'SAN', 'AUS', 'HOU', 'IAH', 
            'MSP', 'DTW', 'CLT', 'DCA', 'BWI', 'IAD', 'SLC', 'MCO', 'TPA',
            'FLL', 'RDU', 'BNA', 'STL', 'CLE', 'PIT', 'CVG', 'IND', 'MKE',
            'MSN', 'GRB', 'MAD', 'LON', 'PAR', 'FRA', 'AMS', 'ZUR', 'DUB'
        ]
        
        # Get origin airports from database
        origin_airports = Airport.query.filter(Airport.iata_code.in_(major_airports)).all()
        origin_codes = [ap.iata_code for ap in origin_airports]
        
        print(f"📊 Using {len(origin_airports)} origin airports")
        print(f"📊 Using {len(airlines)} airlines")
        print(f"📊 Using {len(aircraft_types)} aircraft types")
        
        # Generate flights for the next 24 hours
        now = datetime.now()
        flights_created = 0
        
        # Flight generation patterns for ORD
        flight_patterns = [
            # Domestic routes (more frequent)
            {'origins': ['LAX', 'SFO', 'SEA', 'PDX', 'SAN'], 'frequency': 8, 'duration_range': (240, 300)},
            {'origins': ['JFK', 'LGA', 'EWR', 'BOS', 'DCA', 'BWI'], 'frequency': 12, 'duration_range': (120, 180)},
            {'origins': ['ATL', 'DFW', 'IAH', 'MIA', 'TPA', 'FLL'], 'frequency': 10, 'duration_range': (150, 210)},
            {'origins': ['DEN', 'SLC', 'PHX', 'LAS'], 'frequency': 6, 'duration_range': (180, 240)},
            {'origins': ['MSP', 'DTW', 'CLE', 'PIT', 'IND'], 'frequency': 4, 'duration_range': (90, 150)},
            # International routes (less frequent but important)
            {'origins': ['LON', 'PAR', 'FRA', 'AMS', 'ZUR'], 'frequency': 2, 'duration_range': (480, 540)},
        ]
        
        for pattern in flight_patterns:
            for origin_code in pattern['origins']:
                if origin_code not in origin_codes:
                    continue
                    
                origin_airport = next((ap for ap in origin_airports if ap.iata_code == origin_code), None)
                if not origin_airport:
                    continue
                
                # Generate multiple flights per day for this route
                num_flights = pattern['frequency']
                base_duration = random.choice(pattern['duration_range'])
                
                for i in range(num_flights):
                    try:
                        # Random timing throughout the day
                        departure_hour = random.randint(5, 23)  # 5 AM to 11 PM
                        departure_minute = random.randint(0, 59)
                        
                        # Create departure time
                        departure_time = now.replace(
                            hour=departure_hour, 
                            minute=departure_minute, 
                            second=0, 
                            microsecond=0
                        )
                        
                        # Add some random days (0-2 days ahead)
                        departure_time += timedelta(days=random.randint(0, 2))
                        
                        # Calculate arrival time
                        arrival_time = departure_time + timedelta(minutes=base_duration + random.randint(-30, 30))
                        
                        # Random airline and aircraft
                        airline = random.choice(airlines)
                        aircraft = random.choice(aircraft_types)
                        
                        # Generate realistic flight number
                        flight_number = f"{airline.iata_code}{random.randint(100, 9999)}"
                        
                        # Determine status and delays
                        status_weights = {
                            'ON_TIME': 0.6,    # 60% on time
                            'DELAYED': 0.25,   # 25% delayed
                            'SCHEDULED': 0.1,  # 10% scheduled (future)
                            'BOARDING': 0.05   # 5% boarding
                        }
                        
                        status = random.choices(
                            list(status_weights.keys()), 
                            weights=list(status_weights.values())
                        )[0]
                        
                        # Calculate delays
                        delay_minutes = 0
                        if status == 'DELAYED':
                            delay_minutes = random.randint(15, 120)
                            arrival_time += timedelta(minutes=delay_minutes)
                        elif status == 'BOARDING':
                            delay_minutes = random.randint(-30, 10)
                            arrival_time += timedelta(minutes=delay_minutes)
                        
                        # Create flight record
                        flight = Flight(
                            flight_number=flight_number,
                            airline_id=airline.id,
                            aircraft_id=aircraft.id,
                            origin_airport_id=origin_airport.id,
                            destination_airport_id=ord_airport.id,
                            flight_date=departure_time.date(),
                            scheduled_departure=departure_time,
                            actual_departure=departure_time if status in ['ON_TIME', 'BOARDING'] else None,
                            scheduled_arrival=arrival_time,
                            actual_arrival=arrival_time if status in ['ON_TIME', 'DELAYED'] else None,
                            status=status,
                            gate=f"Gate {random.randint(10, 50)}",
                            terminal=f"Terminal {random.randint(1, 5)}",
                            delay_minutes=delay_minutes,
                            seats_available=random.randint(5, aircraft.capacity // 2),
                            total_seats=aircraft.capacity,
                            load_factor=random.uniform(0.7, 0.95),
                            on_time_probability=random.uniform(0.6, 0.9),
                            delay_probability=random.uniform(0.1, 0.4),
                            cancellation_probability=random.uniform(0.01, 0.05),
                            base_price=random.uniform(200, 800),
                            current_price=random.uniform(200, 800),
                            currency='USD',
                            duration_minutes=base_duration,
                            distance_miles=random.randint(500, 2500)
                        )
                        
                        db.session.add(flight)
                        flights_created += 1
                        
                    except Exception as e:
                        print(f"❌ Error creating flight: {e}")
                        continue
        
        db.session.commit()
        print(f"✅ Successfully created {flights_created} comprehensive ORD flights")
        
        # Show statistics
        total_flights = Flight.query.count()
        print(f"\n📊 Database Statistics:")
        print(f"   Total flights: {total_flights}")
        
        # Show route distribution
        route_stats = db.session.query(
            Airport.iata_code,
            db.func.count(Flight.id).label('count')
        ).join(
            Flight, Airport.id == Flight.origin_airport_id
        ).group_by(Airport.iata_code).order_by(
            db.desc('count')
        ).limit(10).all()
        
        print(f"\n🛫 Top 10 Routes to ORD:")
        for route in route_stats:
            print(f"   {route.iata_code} → ORD: {route.count} flights")
        
        # Show airline distribution
        airline_stats = db.session.query(
            Airline.name,
            db.func.count(Flight.id).label('count')
        ).join(
            Flight, Airline.id == Flight.airline_id
        ).group_by(Airline.name).order_by(
            db.desc('count')
        ).limit(10).all()
        
        print(f"\n✈️  Top 10 Airlines:")
        for airline in airline_stats:
            print(f"   {airline.name}: {airline.count} flights")
        
        # Show status distribution
        status_stats = db.session.query(
            Flight.status,
            db.func.count(Flight.id).label('count')
        ).group_by(Flight.status).all()
        
        print(f"\n📈 Flight Status Distribution:")
        for status in status_stats:
            print(f"   {status.status}: {status.count} flights")

def main():
    """Main function to generate comprehensive ORD flights."""
    print("🚀 Generating Comprehensive ORD Flight Data")
    print("=" * 60)
    print("🏢 Chicago O'Hare (ORD) - One of the World's Busiest Airports")
    print("📊 Generating realistic flight patterns and schedules...")
    print("=" * 60)
    
    try:
        generate_comprehensive_ord_flights()
        
        print(f"\n🎉 ORD Flight Data Generation Complete!")
        print(f"🌐 Your OnTime program now has comprehensive ORD flight data!")
        print(f"🔍 Try searching different routes to see the variety of flights")
        print(f"📱 Visit http://localhost:3000 to explore the data")
        
    except Exception as e:
        print(f"\n❌ Error generating flights: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
