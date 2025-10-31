# Monthly Airline Delay Prediction Feature

## Overview

The Monthly Airline Delay Prediction feature allows users to view delay predictions for specific airlines and months based on historical on-time performance data from FAA/BTS and Cirium sources.

## Features

### 1. Monthly Performance Analysis
- Select any airline and month combination
- View delay predictions with three risk categories (LOW, MEDIUM, HIGH)
- See percentage probability of delays
- Get predicted delay duration
- View completion factors and on-time percentages

### 2. Delay Cause Breakdown
Visual breakdown of delay causes:
- National Air System (NAS) delays - blue
- Carrier delays - red
- Late Aircraft delays - orange
- Weather delays - green
- Security delays - purple

### 3. Risk Categorization
- **LOW**: < 15% delay probability
- **MEDIUM**: 15-30% delay probability  
- **HIGH**: > 30% delay probability

## Database Model

### AirlineMonthlyPerformance

Stores monthly performance statistics for airlines:

```python
- year, month
- airline_id, airport_id (optional)
- total_arrivals, arrivals_delayed_15_min
- Delay counts by cause (carrier, weather, NAS, security, late aircraft)
- Cancellations, diversions
- Delay minutes by cause
- on_time_percentage, completion_factor
```

## API Endpoints

### Get Airlines
```
GET /api/airlines
```
Returns list of all airlines with performance data.

### Get Available Months
```
GET /api/airline-performance/available-months
```
Returns list of year-month combinations with available data.

### Get Monthly Prediction
```
GET /api/airline-performance/predict?year=2025&month=6&airline=DL
```
Returns delay prediction for specified airline and month.

**Response includes:**
- Airline information
- Delay probability and risk category
- Predicted delay duration
- On-time percentage
- Completion factor
- Cancellation rate
- Delay causes breakdown
- Historical basis information

### Get Monthly Performance
```
GET /api/airline-performance/monthly?year=2025&month=5&airline=DL
```
Returns raw performance statistics for specified period.

## Data Sources

### 1. Delta May 2025 ORD Data
Example data showing delay causes:
- Carrier: 109.64 flights, 9,424 minutes
- Weather: 8.64 flights, 1,712 minutes
- NAS: 176.78 flights, 14,802 minutes
- Late Aircraft: 71.95 flights, 5,841 minutes
- Total: 1,078 arrivals, 367 delayed

### 2. Cirium North America May 2025
On-time performance rankings:
1. Air Canada (AC): 79.06%
2. Delta Air Lines (DL): 79.03%
3. Alaska Airlines (AS): 78.65%
4. United Airlines (UA): 77.42%
5. WestJet (WS): 76.73%
6. JetBlue (B6): 76.28%
7. Spirit Airlines (NK): 75.84%
8. American Airlines (AA): 75.41%
9. Southwest Airlines (WN): 75.36%
10. Frontier Airlines (F9): 69.94%

## Usage

### Import Data

```bash
# Import example data (Delta May 2025 + Cirium data)
python import_airline_performance.py

# Import from CSV file
python import_airline_performance.py path/to/data.csv
```

### Access Dashboard

1. Start backend server:
```bash
python app.py
```

2. Start frontend dev server:
```bash
cd frontend
npm run dev
```

3. Navigate to Monthly Dashboard:
- Click "Monthly Analysis" button on main dashboard
- Or visit: http://localhost:3000/monthly

### Select Parameters

1. Choose an airline from dropdown
2. Select a month from available options
3. View predictions and analytics

## Prediction Algorithm

Current implementation uses historical averages:
1. Load last 12 months of data for selected airline
2. Calculate average delay rate
3. Calculate average delay minutes per flight
4. Compute delay causes distribution
5. Apply risk categorization

### Future Enhancements

- Machine learning models trained on historical data
- Seasonal adjustments
- Weather impact predictions
- Route-specific analysis
- Airport-specific analysis
- Multi-month trends

## Adding More Data

### From FAA/BTS

1. Visit: https://www.transtats.bts.gov
2. Download monthly On-Time Performance data
3. Aggregate by airline and month
4. Create CSV with following columns:
   - year, month, carrier, carline_name
   - total_arrivals, arrivals_delayed_15_min
   - carrier_delay_count, weather_delay_count, nas_delay_count
   - security_delay_count, late_aircraft_delay_count
   - cancellations, diversions
   - total_delay_minutes
   - carrier_delay_minutes, weather_delay_minutes, nas_delay_minutes
   - security_delay_minutes, late_aircraft_delay_minutes
   - on_time_percentage, completion_factor

5. Import:
```bash
python import_airline_performance.py your_file.csv
```

### From Cirium

1. Download monthly reports
2. Extract airline statistics
3. Manually add to `import_airline_performance.py`
4. Or create CSV and import

## Frontend Components

### Monthly Dashboard (`/monthly/page.tsx`)
- Airline and month selectors
- Delay prediction display with risk categorization
- Delay causes breakdown chart
- Metrics cards (completion factor, cancellation rate, on-time %)

### Navigation
- Link from main dashboard header
- Back button on monthly dashboard
- Glassmorphic design consistent with main app

## Files Modified/Created

### New Files
- `models.py` - Added `AirlineMonthlyPerformance` model
- `import_airline_performance.py` - Data import script
- `frontend/src/app/monthly/page.tsx` - Monthly dashboard
- `DATA_IMPORT_GUIDE.md` - Detailed data import guide
- `MONTHLY_PREDICTION_README.md` - This file

### Modified Files
- `app.py` - Added API endpoints for monthly predictions
- `frontend/src/lib/api.ts` - Added API client functions
- `frontend/src/app/page.tsx` - Added navigation link

## Testing

### Test API Endpoints

```bash
# Get airlines
curl http://localhost:8000/api/airlines

# Get available months
curl http://localhost:8000/api/airline-performance/available-months

# Get prediction for Delta June 2025
curl http://localhost:8000/api/airline-performance/predict?year=2025&month=6&airline=DL
```

### Expected Response for Prediction

```json
{
  "airline": {
    "code": "DL",
    "name": "Delta Air Lines"
  },
  "year": 2025,
  "month": 6,
  "prediction": {
    "delay_probability": 21.0,
    "delay_risk_category": "MEDIUM",
    "delay_risk_color": "yellow",
    "predicted_delay_duration_minutes": 20.0,
    "predicted_delay_duration_formatted": "19 min",
    "delay_duration_category": "LOW"
  },
  "metrics": {
    "estimated_completion_factor": 99.69,
    "estimated_cancellation_rate": 1.84,
    "on_time_percentage": 79.03
  },
  "delay_causes": [
    {
      "cause": "National Air System",
      "percentage": 47.0,
      "color": "#3b82f6"
    },
    ...
  ],
  "historical_basis": {
    "months_analyzed": 2,
    "latest_data": {
      "year": 2025,
      "month": 5,
      "on_time_percentage": 79.03,
      "completion_factor": 99.4
    }
  }
}
```

## Next Steps

1. **Add More Historical Data**
   - Import data for multiple months/years
   - Include more airlines
   - Add airport-specific data

2. **Enhance Predictions**
   - Train ML models on historical data
   - Factor in seasonal patterns
   - Consider weather forecasts
   - Include route-specific factors

3. **Advanced Visualizations**
   - Trend charts over time
   - Comparison between airlines
   - Regional/national averages
   - Heat maps

4. **User Features**
   - Bookmark favorite airlines
   - Historical comparisons
   - Alert preferences
   - Export reports

## References

- **FAA/BTS**: https://www.transtats.bts.gov
- **Cirium**: https://www.cirium.com/resources/on-time-performance/
- **DOT Reports**: https://www.transportation.gov/airconsumer/air-travel-consumer-reports

