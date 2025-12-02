"""
Fix Airline Matching for Flights
=================================

This script matches flight numbers to airline IATA codes properly.
Flight numbers start with airline IATA codes (e.g., "AA1234" -> American Airlines "AA").
"""

from models import db, Flight, Airline
from app import app

def fix_airline_matching():
    """Fix airline matching for all flights based on flight number prefix."""
    print("🔧 Fixing airline matching for flights...")
    
    with app.app_context():
        # Get all flights
        flights = Flight.query.all()
        print(f"📊 Found {len(flights)} flights to check")
        
        fixed_count = 0
        not_found_count = 0
        
        for flight in flights:
            if not flight.flight_number or len(flight.flight_number) < 2:
                continue
            
            # Extract airline code from flight number
            # Try 2 characters first, then 3 characters (for some airlines)
            flight_number_prefix_2 = flight.flight_number[:2].upper()
            flight_number_prefix_3 = flight.flight_number[:3].upper() if len(flight.flight_number) >= 3 else None
            
            # Find airline by IATA code (try 2-char first)
            airline = Airline.query.filter_by(iata_code=flight_number_prefix_2).first()
            
            # If not found, try 3-character code
            if not airline and flight_number_prefix_3:
                airline = Airline.query.filter_by(iata_code=flight_number_prefix_3).first()
            
            if airline:
                if flight.airline_id != airline.id:
                    # Update flight's airline
                    old_airline = flight.airline.name if flight.airline else "Unknown"
                    flight.airline_id = airline.id
                    fixed_count += 1
                    if fixed_count % 100 == 0:
                        print(f"   Fixed {fixed_count} flights...")
            else:
                # Try to find by partial match or create mapping
                # Comprehensive airline code mappings (North American airlines)
                airline_mappings = {
                    'DL': 'Delta Air Lines',
                    'AA': 'American Airlines',
                    'UA': 'United Airlines',
                    'WN': 'Southwest Airlines',
                    'AS': 'Alaska Airlines',
                    'B6': 'JetBlue Airways',
                    'NK': 'Spirit Airlines',
                    'F9': 'Frontier Airlines',
                    'AC': 'Air Canada',
                    'WS': 'WestJet',
                    'G4': 'Allegiant Air',
                    'SY': 'Sun Country Airlines',
                    'YX': 'Republic Airways',
                    'MQ': 'Envoy Air',
                    'OH': 'PSA Airlines',
                    'YX': 'Republic Airways',
                    '9E': 'Endeavor Air',
                    'CP': 'Compass Airlines',
                    'OO': 'SkyWest Airlines',
                    'QX': 'Horizon Air',
                    'YV': 'Mesa Airlines',
                    'EV': 'ExpressJet',
                    'ZW': 'Air Wisconsin',
                    'C5': 'Champlain Enterprises',
                    'PT': 'Piedmont Airlines',
                    'KS': 'Peninsula Airways',
                    'VX': 'Virgin America',
                    'HA': 'Hawaiian Airlines',
                }
                
                # Try 2-char code first, then 3-char
                flight_number_prefix = flight_number_prefix_2
                if flight_number_prefix not in airline_mappings and flight_number_prefix_3:
                    flight_number_prefix = flight_number_prefix_3
                
                if flight_number_prefix in airline_mappings:
                    airline_name = airline_mappings[flight_number_prefix]
                    airline = Airline.query.filter_by(name=airline_name).first()
                    if airline:
                        flight.airline_id = airline.id
                        fixed_count += 1
                    else:
                        # Create airline if it doesn't exist
                        new_airline = Airline(
                            iata_code=flight_number_prefix_2,  # Use 2-char for IATA
                            icao_code=flight_number_prefix_2,
                            name=airline_name,
                            country='United States' if flight_number_prefix_2 not in ['AC', 'WS'] else 'Canada'
                        )
                        db.session.add(new_airline)
                        db.session.flush()
                        flight.airline_id = new_airline.id
                        fixed_count += 1
                else:
                    not_found_count += 1
        
        db.session.commit()
        
        print(f"\n✅ Fixed {fixed_count} flights")
        if not_found_count > 0:
            print(f"⚠️  Could not match {not_found_count} flights")
        
        # Show summary
        unknown_airlines = db.session.query(Flight).join(Airline).filter(
            Airline.name.like('%Unknown%')
        ).count()
        print(f"📊 Flights with 'Unknown' airline: {unknown_airlines}")

if __name__ == '__main__':
    fix_airline_matching()

