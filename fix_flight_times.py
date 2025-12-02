"""
Fix Flight Times
================

This script fixes flights where scheduled_arrival equals scheduled_departure
by calculating arrival time from departure + duration_minutes.
"""

from datetime import timedelta
from models import db, Flight
from app import app

def fix_flight_times():
    """Fix flights where arrival time equals departure time."""
    print("🔧 Fixing flight times...")
    
    with app.app_context():
        # Find flights where scheduled_arrival == scheduled_departure
        all_flights = Flight.query.all()
        print(f"📊 Checking {len(all_flights)} flights...")
        
        fixed_count = 0
        no_duration_count = 0
        
        for flight in all_flights:
            # Check if arrival equals departure (or very close - within 1 minute)
            if flight.scheduled_departure and flight.scheduled_arrival:
                time_diff = abs((flight.scheduled_arrival - flight.scheduled_departure).total_seconds())
                
                # If arrival is same as departure (or within 1 minute), fix it
                if time_diff < 60:  # Less than 1 minute difference
                    # Use duration_minutes if available
                    if flight.duration_minutes and flight.duration_minutes > 0:
                        flight.scheduled_arrival = flight.scheduled_departure + timedelta(minutes=flight.duration_minutes)
                        fixed_count += 1
                    else:
                        # Calculate duration based on route distance
                        # Default durations by route type (rough estimates)
                        default_duration = 180  # 3 hours default
                        
                        # If we have distance, estimate duration
                        if flight.distance_miles:
                            # Rough estimate: 500 mph average speed
                            estimated_duration = int(flight.distance_miles / 500 * 60)
                            flight.duration_minutes = estimated_duration
                            flight.scheduled_arrival = flight.scheduled_departure + timedelta(minutes=estimated_duration)
                        else:
                            # Use default
                            flight.duration_minutes = default_duration
                            flight.scheduled_arrival = flight.scheduled_departure + timedelta(minutes=default_duration)
                        
                        fixed_count += 1
                        no_duration_count += 1
                    
                    # Also fix actual_arrival if it exists and equals actual_departure
                    if flight.actual_departure and flight.actual_arrival:
                        actual_diff = abs((flight.actual_arrival - flight.actual_departure).total_seconds())
                        if actual_diff < 60 and flight.duration_minutes:
                            flight.actual_arrival = flight.actual_departure + timedelta(minutes=flight.duration_minutes)
            
            # Also ensure duration_minutes is set if not present
            if not flight.duration_minutes and flight.scheduled_departure and flight.scheduled_arrival:
                duration = (flight.scheduled_arrival - flight.scheduled_departure).total_seconds() / 60
                if duration > 0:
                    flight.duration_minutes = int(duration)
        
        db.session.commit()
        
        print(f"\n✅ Fixed {fixed_count} flights")
        if no_duration_count > 0:
            print(f"   {no_duration_count} flights had no duration and were assigned default/estimated duration")
        
        # Show summary
        still_broken = Flight.query.filter(
            db.func.abs(
                db.func.extract('epoch', Flight.scheduled_arrival - Flight.scheduled_departure)
            ) < 60
        ).count()
        print(f"📊 Flights with same departure/arrival times remaining: {still_broken}")

if __name__ == '__main__':
    fix_flight_times()

