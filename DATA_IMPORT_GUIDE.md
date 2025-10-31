# Airline Performance Data Import Guide

This guide explains how to obtain and import monthly airline on-time performance data from FAA/BTS and Cirium sources.

## Data Sources

### 1. Bureau of Transportation Statistics (BTS)

The BTS provides detailed monthly airline performance data through their TranStats portal.

**Website:** https://www.transtats.bts.gov

**Data Available:**
- On-Time Performance data by airline
- Delay causes (Carrier, Weather, NAS, Security, Late Aircraft)
- Cancellations and diversions
- Completion factors
- On-time percentages

**How to Download:**

1. Visit: https://www.transtats.bts.gov/DL_SelectFields.aspx?Table_ID=236
2. Select the following fields:
   - Year
   - Month
   - Carrier (Airline code)
   - ArrDel15 (Flights delayed 15+ minutes)
   - CarrierCT (Carrier delay count)
   - WeatherCT (Weather delay count)
   - NASCT (National Air System delay count)
   - SecurityCT (Security delay count)
   - LateAircraftCT (Late aircraft delay count)
   - Cancelled
   - Diverted
   - CarrierDelay (Carrier delay minutes)
   - WeatherDelay (Weather delay minutes)
   - NASDelay (NAS delay minutes)
   - SecurityDelay (Security delay minutes)
   - LateAircraftDelay (Late aircraft delay minutes)

3. Select year and month range
4. Click "Download" to get CSV file

**Note:** The BTS data is structured per-flight, so you'll need to aggregate it by airline and month.

### 2. Cirium Monthly Reports

Cirium provides monthly on-time performance reports for airlines and airports.

**Website:** https://www.cirium.com/resources/on-time-performance/

**Data Available:**
- On-time arrival percentages
- Completion factors
- Total flights tracked
- Rankings

**Limitation:** Cirium reports don't include detailed delay cause breakdowns.

### 3. DOT Air Travel Consumer Reports

U.S. Department of Transportation publishes monthly consumer reports.

**Website:** https://www.transportation.gov/airconsumer/air-travel-consumer-reports

**Data Available:**
- Summary statistics
- On-time performance rates
- Cancellation rates
- Consumer complaints

## Importing Data

### Method 1: Using the Import Script

The `import_airline_performance.py` script includes:

1. **Delta May 2025 Data** - Hardcoded example data
2. **Cirium May 2025 Data** - Aggregated North America data
3. **CSV Import** - Generic CSV file importer

**Run the script:**

```bash
# Import example data
python import_airline_performance.py

# Import from CSV file
python import_airline_performance.py path/to/data.csv
```

### Method 2: Creating Aggregated CSV Files

For BTS data, you'll need to aggregate it by airline and month:

**Example CSV format:**

```csv
year,month,carrier,carline_name,total_arrivals,arrivals_delayed_15_min,carrier_delay_count,weather_delay_count,nas_delay_count,security_delay_count,late_aircraft_delay_count,cancellations,diversions,total_delay_minutes,carrier_delay_minutes,weather_delay_minutes,nas_delay_minutes,security_delay_minutes,late_aircraft_delay_minutes,on_time_percentage,completion_factor
2025,5,DL,Delta Air Lines,1078,367,109.64,8.64,176.78,0,71.95,29,12,31779,9424,1712,14802,0,5841,79.03,99.40
2025,5,AA,American Airlines,5000,1250,375,25,500,0,350,50,20,75000,22500,1500,37500,0,13500,75.00,98.00
```

### Method 3: Direct Database Insertion

You can also manually insert data using SQL or Python:

```python
from app import app
from models import db, Airline, AirlineMonthlyPerformance

with app.app_context():
    # Get airline
    airline = Airline.query.filter_by(iata_code='DL').first()
    
    # Create performance record
    performance = AirlineMonthlyPerformance(
        year=2025,
        month=6,
        airline_id=airline.id,
        total_arrivals=1000,
        arrivals_delayed_15_min=200,
        # ... other fields
    )
    
    db.session.add(performance)
    db.session.commit()
```

## Data Available in Current Database

The import script includes:

### May 2025 Data

**Delta Air Lines at ORD:**
- Total Arrivals: 1,078
- Delayed 15+ min: 367
- On-Time %: 79.03%
- Completion Factor: 99.40%

**Cirium North America Airlines:**
- Air Canada (AC): 79.06% on-time, 32,723 flights
- Delta Air Lines (DL): 79.03% on-time, 156,730 flights
- Alaska Airlines (AS): 78.65% on-time, 39,511 flights
- United Airlines (UA): 77.42% on-time, 147,092 flights
- WestJet (WS): 76.73% on-time, 17,511 flights
- JetBlue (B6): 76.28% on-time, 26,102 flights
- Spirit Airlines (NK): 75.84% on-time, 19,575 flights
- American Airlines (AA): 75.41% on-time, 196,254 flights
- Southwest Airlines (WN): 75.36% on-time, 122,605 flights
- Frontier Airlines (F9): 69.94% on-time, 17,140 flights

## Adding Historical Data

To add historical data:

1. Download monthly BTS data files
2. Aggregate by airline and month
3. Create CSV files with the format above
4. Run: `python import_airline_performance.py your_file.csv`

For more months, repeat this process for each month/year combination.

## Verification

Check imported data:

```bash
# Run the import script to see summary
python import_airline_performance.py
```

The script will show:
- Total performance records
- Number of unique airlines
- Time periods covered

## Troubleshooting

**Issue: Database locked**
- Solution: Close any apps using the database

**Issue: Duplicate data**
- Solution: The script skips existing records. Delete duplicates manually if needed.

**Issue: Missing airlines**
- Solution: The script auto-creates airlines if they don't exist

**Issue: Missing airports**
- Solution: The script creates placeholder airports for airport-specific data

## Next Steps

After importing data:

1. Create the API endpoint to serve this data
2. Build the frontend components for visualization
3. Implement delay prediction logic based on historical data

