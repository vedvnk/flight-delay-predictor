"""
Import Airline Monthly Performance Data
========================================

This script imports monthly airline on-time performance data from FAA/BTS sources.
The data includes delay causes, completion factors, and other metrics.
"""

import os
import sys
from datetime import datetime
import pandas as pd
from models import db, Airline, Airport, AirlineMonthlyPerformance
from app import app

def get_or_create_airline(iata_code: str, name: str):
    """Get existing airline or create new one."""
    airline = Airline.query.filter_by(iata_code=iata_code).first()
    if not airline:
        airline = Airline(
            iata_code=iata_code,
            icao_code=iata_code,  # Using IATA as ICAO for now
            name=name,
            country='United States'
        )
        db.session.add(airline)
        db.session.flush()
    return airline

def get_or_create_airport(iata_code: str):
    """Get existing airport or create placeholder."""
    airport = Airport.query.filter_by(iata_code=iata_code).first()
    if not airport:
        # Create a placeholder airport
        airport = Airport(
            iata_code=iata_code,
            icao_code=iata_code,
            name=f"{iata_code} Airport",
            city="Unknown",
            state="Unknown",
            country="United States",
            latitude=0.0,
            longitude=0.0,
            timezone="UTC"
        )
        db.session.add(airport)
        db.session.flush()
    return airport

def import_delta_may_2025():
    """
    Import Delta Air Lines May 2025 data based on the provided statistics.
    This is example data showing the structure.
    """
    print("📊 Importing Delta Air Lines May 2025 Performance Data...")
    
    with app.app_context():
        # Get or create Delta
        delta = get_or_create_airline('DL', 'Delta Air Lines')
        
        # Get or create ORD airport
        ord = get_or_create_airport('ORD')
        
        # Check if data already exists
        existing = AirlineMonthlyPerformance.query.filter_by(
            year=2025,
            month=5,
            airline_id=delta.id,
            airport_id=ord.id
        ).first()
        
        if existing:
            print("⚠️  Data already exists for Delta May 2025 at ORD. Skipping...")
            return
        
        # Create performance record based on the data provided
        # Delta May 2025 ORD data:
        performance = AirlineMonthlyPerformance(
            year=2025,
            month=5,
            airline_id=delta.id,
            airport_id=ord.id,
            total_arrivals=1078,
            arrivals_delayed_15_min=367,
            
            # Delay counts
            carrier_delay_count=109.64,
            weather_delay_count=8.64,
            nas_delay_count=176.78,
            security_delay_count=0,
            late_aircraft_delay_count=71.95,
            
            # Cancellations and diversions
            cancellations=29,
            diversions=12,
            
            # Total delay minutes
            total_delay_minutes=31779,
            
            # Delay minutes by cause
            carrier_delay_minutes=9424,
            weather_delay_minutes=1712,
            nas_delay_minutes=14802,
            security_delay_minutes=0,
            late_aircraft_delay_minutes=5841,
            
            # Performance metrics
            on_time_percentage=79.03,  # From Cirium data
            completion_factor=99.40
        )
        
        db.session.add(performance)
        db.session.commit()
        print("✅ Imported Delta May 2025 data successfully")
        print(f"   Total Arrivals: {performance.total_arrivals}")
        print(f"   Delayed 15+ min: {performance.arrivals_delayed_15_min}")
        print(f"   On-Time %: {performance.on_time_percentage}%")

def import_cirium_data():
    """
    Import Cirium North America On-Time Performance data for May 2025.
    This includes data for multiple airlines.
    """
    print("\n📊 Importing Cirium May 2025 North America Performance Data...")
    
    with app.app_context():
        # Get ORD airport
        ord = get_or_create_airport('ORD')
        
        # Cirium North America May 2025 data
        cirium_data = [
            # (IATA, Name, On-Time %, Completion Factor, Total Flights)
            ('AC', 'Air Canada', 79.06, 99.84, 32723),
            ('DL', 'Delta Air Lines', 79.03, 99.98, 156730),
            ('AS', 'Alaska Airlines', 78.65, 99.98, 39511),
            ('UA', 'United Airlines', 77.42, 99.97, 147092),
            ('WS', 'WestJet', 76.73, 99.94, 17511),
            ('B6', 'JetBlue', 76.28, 99.32, 26102),
            ('NK', 'Spirit Airlines', 75.84, 97.54, 19575),
            ('AA', 'American Airlines', 75.41, 99.97, 196254),
            ('WN', 'Southwest Airlines', 75.36, 99.86, 122605),
            ('F9', 'Frontier Airlines', 69.94, 99.46, 17140),
        ]
        
        imported_count = 0
        for iata_code, name, on_time_pct, completion_factor, total_flights in cirium_data:
            # Get or create airline
            airline = get_or_create_airline(iata_code, name)
            
            # Check if data exists
            existing = AirlineMonthlyPerformance.query.filter_by(
                year=2025,
                month=5,
                airline_id=airline.id,
                airport_id=None  # Global performance, not airport-specific
            ).first()
            
            if existing:
                print(f"⚠️  Data already exists for {name} May 2025. Skipping...")
                continue
            
            # Calculate delayed flights (approximate based on on-time percentage)
            delayed_flights = int(total_flights * (100 - on_time_pct) / 100)
            
            # Create performance record
            # Note: We don't have detailed delay cause data from Cirium, so we'll use estimates
            # based on Delta's distribution
            nas_delay_count = delayed_flights * 0.48  # Based on Delta's distribution
            carrier_delay_count = delayed_flights * 0.30
            late_aircraft_delay_count = delayed_flights * 0.20
            weather_delay_count = delayed_flights * 0.02
            
            # Estimate delay minutes (average 50 minutes per delayed flight)
            total_delay_minutes = delayed_flights * 50
            
            performance = AirlineMonthlyPerformance(
                year=2025,
                month=5,
                airline_id=airline.id,
                airport_id=None,  # Global performance
                total_arrivals=total_flights,
                arrivals_delayed_15_min=delayed_flights,
                
                # Estimated delay counts
                nas_delay_count=nas_delay_count,
                carrier_delay_count=carrier_delay_count,
                late_aircraft_delay_count=late_aircraft_delay_count,
                weather_delay_count=weather_delay_count,
                security_delay_count=0,
                
                # Cancellations (estimated)
                cancellations=int(total_flights * 0.01),
                diversions=int(total_flights * 0.001),
                
                # Delay minutes
                total_delay_minutes=total_delay_minutes,
                nas_delay_minutes=int(total_delay_minutes * 0.47),
                carrier_delay_minutes=int(total_delay_minutes * 0.30),
                late_aircraft_delay_minutes=int(total_delay_minutes * 0.20),
                weather_delay_minutes=int(total_delay_minutes * 0.03),
                security_delay_minutes=0,
                
                # Performance metrics
                on_time_percentage=on_time_pct,
                completion_factor=completion_factor
            )
            
            db.session.add(performance)
            db.session.flush()
            imported_count += 1
            print(f"✅ Imported {name} ({iata_code}): {on_time_pct}% on-time, {total_flights} flights")
        
        db.session.commit()
        print(f"\n✅ Successfully imported {imported_count} airline records for May 2025")

def import_csv_data(csv_path: str):
    """
    Import airline performance data from a CSV file.
    
    CSV format should have columns:
    - year, month, carrier (or iata_code)
    - total_arrivals, arrivals_delayed_15_min
    - carrier_delay_count, weather_delay_count, nas_delay_count, 
      security_delay_count, late_aircraft_delay_count
    - cancellations, diversions
    - total_delay_minutes
    - carrier_delay_minutes, weather_delay_minutes, nas_delay_minutes,
      security_delay_minutes, late_aircraft_delay_minutes
    - on_time_percentage, completion_factor
    """
    print(f"\n📊 Importing data from {csv_path}...")
    
    if not os.path.exists(csv_path):
        print(f"❌ File not found: {csv_path}")
        return
    
    try:
        df = pd.read_csv(csv_path)
        print(f"✅ Loaded {len(df)} records from CSV")
        
        with app.app_context():
            imported = 0
            for _, row in df.iterrows():
                try:
                    # Get airline
                    iata_code = row.get('carrier') or row.get('iata_code')
                    airline_name = row.get('carline_name') or row.get('airline_name') or f"Airline {iata_code}"
                    airline = get_or_create_airline(iata_code, airline_name)
                    
                    # Get airport if specified
                    airport = None
                    if 'airport' in row and pd.notna(row['airport']):
                        airport = get_or_create_airport(row['airport'])
                    
                    # Check if exists
                    existing = AirlineMonthlyPerformance.query.filter_by(
                        year=int(row['year']),
                        month=int(row['month']),
                        airline_id=airline.id,
                        airport_id=airport.id if airport else None
                    ).first()
                    
                    if existing:
                        print(f"⚠️  Skipping existing record: {iata_code} {row['year']}-{row['month']}")
                        continue
                    
                    # Create performance record
                    performance = AirlineMonthlyPerformance(
                        year=int(row['year']),
                        month=int(row['month']),
                        airline_id=airline.id,
                        airport_id=airport.id if airport else None,
                        total_arrivals=int(row['total_arrivals']) if pd.notna(row.get('total_arrivals')) else None,
                        arrivals_delayed_15_min=int(row['arrivals_delayed_15_min']) if pd.notna(row.get('arrivals_delayed_15_min')) else None,
                        
                        carrier_delay_count=float(row['carrier_delay_count']) if pd.notna(row.get('carrier_delay_count')) else None,
                        weather_delay_count=float(row['weather_delay_count']) if pd.notna(row.get('weather_delay_count')) else None,
                        nas_delay_count=float(row['nas_delay_count']) if pd.notna(row.get('nas_delay_count')) else None,
                        security_delay_count=float(row['security_delay_count']) if pd.notna(row.get('security_delay_count')) else None,
                        late_aircraft_delay_count=float(row['late_aircraft_delay_count']) if pd.notna(row.get('late_aircraft_delay_count')) else None,
                        
                        cancellations=int(row['cancellations']) if pd.notna(row.get('cancellations')) else None,
                        diversions=int(row['diversions']) if pd.notna(row.get('diversions')) else None,
                        
                        total_delay_minutes=int(row['total_delay_minutes']) if pd.notna(row.get('total_delay_minutes')) else None,
                        carrier_delay_minutes=int(row['carrier_delay_minutes']) if pd.notna(row.get('carrier_delay_minutes')) else None,
                        weather_delay_minutes=int(row['weather_delay_minutes']) if pd.notna(row.get('weather_delay_minutes')) else None,
                        nas_delay_minutes=int(row['nas_delay_minutes']) if pd.notna(row.get('nas_delay_minutes')) else None,
                        security_delay_minutes=int(row['security_delay_minutes']) if pd.notna(row.get('security_delay_minutes')) else None,
                        late_aircraft_delay_minutes=int(row['late_aircraft_delay_minutes']) if pd.notna(row.get('late_aircraft_delay_minutes')) else None,
                        
                        on_time_percentage=float(row['on_time_percentage']) if pd.notna(row.get('on_time_percentage')) else None,
                        completion_factor=float(row['completion_factor']) if pd.notna(row.get('completion_factor')) else None,
                    )
                    
                    db.session.add(performance)
                    imported += 1
                    
                except Exception as e:
                    print(f"❌ Error processing row: {str(e)}")
                    continue
            
            db.session.commit()
            print(f"✅ Successfully imported {imported} records from CSV")
            
    except Exception as e:
        print(f"❌ Error importing CSV: {str(e)}")

def main():
    """Main function to import airline performance data."""
    print("=" * 60)
    print("Airline Monthly Performance Data Import")
    print("=" * 60)
    
    with app.app_context():
        db.create_all()
        
        # Import Delta specific data
        import_delta_may_2025()
        
        # Import Cirium data
        import_cirium_data()
        
        # If CSV file provided, import from it
        if len(sys.argv) > 1:
            csv_path = sys.argv[1]
            import_csv_data(csv_path)
    
    print("\n" + "=" * 60)
    print("✅ Import complete!")
    print("=" * 60)
    
    # Show summary
    with app.app_context():
        total_records = AirlineMonthlyPerformance.query.count()
        print(f"\n📊 Total performance records in database: {total_records}")
        
        # Show unique airlines
        airlines = db.session.query(AirlineMonthlyPerformance.airline_id).distinct().count()
        print(f"📊 Airlines in database: {airlines}")
        
        # Show year-month combinations
        periods = db.session.query(
            AirlineMonthlyPerformance.year, 
            AirlineMonthlyPerformance.month
        ).distinct().all()
        print(f"📊 Time periods covered: {len(periods)}")
        for year, month in sorted(periods):
            print(f"   - {year}-{month:02d}")

if __name__ == '__main__':
    main()

