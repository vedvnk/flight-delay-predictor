# How to Run the Flight Delay Predictor Dashboard

## Prerequisites

- Python 3.9+ installed
- Node.js 18+ installed
- npm or yarn installed

## Step 1: Setup Backend (Flask API)

### 1.1 Install Python Dependencies

```bash
cd /Users/veda/Downloads/flight-delay-predictor
pip install -r requirements.txt
```

### 1.2 Initialize Database (if not already done)

```bash
# Initialize the database with airports, airlines, and flights
python init_db.py

# Import airline performance data (historical data from 2022-2030)
python import_airline_performance.py

# Generate historical performance data (if needed)
python generate_historical_performance_data.py all
```

### 1.3 Start Backend Server

```bash
python app.py
```

The backend will start at **http://localhost:8000**

You should see:
```
✅ Database connected successfully with X flights
✅ ML models loaded successfully
 * Running on http://127.0.0.1:8000
```

## Step 2: Setup Frontend (Next.js Dashboard)

### 2.1 Install Node Dependencies

Open a **new terminal window** and run:

```bash
cd /Users/veda/Downloads/flight-delay-predictor/frontend
npm install
```

### 2.2 Start Frontend Development Server

```bash
npm run dev
```

The frontend will start at **http://localhost:3000**

You should see:
```
▲ Next.js 15.0.3
- Local:        http://localhost:3000
✓ Ready in Xms
```

## Step 3: Access the Dashboard

1. **Main Dashboard**: Open your browser and go to:
   - http://localhost:3000

2. **Monthly Analysis Dashboard**: 
   - Click "Monthly Analysis" button in the header, or
   - Go directly to: http://localhost:3000/monthly

## Features Available

### Main Dashboard (`/`)
- Search flights by route (From/To airports) and date
- View individual flight predictions with:
  - Risk level (Low/Medium/High) with color coding
  - Predicted delay percentage
  - Expected delay duration
  - Flight status and gate information

### Monthly Analysis Dashboard (`/monthly`)
- Select airline and month/year
- View monthly performance metrics:
  - Chance of delay (based on FAA/Cirium data)
  - On-time percentage
  - Completion factor
  - Cancellation rate
  - Delay causes breakdown (Weather, NAS, Carrier, etc.)

## Troubleshooting

### Backend Issues

**Database not initialized:**
```bash
python init_db.py
```

**ML models not found:**
```bash
python train_ml_models.py
```

**Port 8000 already in use:**
- Change the port in `app.py`:
  ```python
  app.run(debug=True, port=8001)  # Use different port
  ```
- Update frontend API URL accordingly

### Frontend Issues

**Port 3000 already in use:**
- Next.js will automatically use the next available port (3001, 3002, etc.)
- Check the terminal output for the actual port

**API connection errors:**
- Make sure backend is running on http://localhost:8000
- Check that `NEXT_PUBLIC_API_BASE_URL` in frontend is set correctly
- Default is `http://localhost:8000` (set in `frontend/src/lib/api.ts`)

**Module not found errors:**
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

## Quick Start (All in One)

If you want to run everything quickly:

### Terminal 1 - Backend:
```bash
cd /Users/veda/Downloads/flight-delay-predictor
python app.py
```

### Terminal 2 - Frontend:
```bash
cd /Users/veda/Downloads/flight-delay-predictor/frontend
npm run dev
```

Then open **http://localhost:3000** in your browser!

## Environment Variables (Optional)

### Backend
No environment variables required by default. Database is stored in `instance/ontime.db`

### Frontend
- `NEXT_PUBLIC_API_BASE_URL`: API base URL (default: `http://localhost:8000`)
- Set in `frontend/src/lib/api.ts` or create `.env.local`:
  ```
  NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
  ```

## Stopping the Servers

- **Backend**: Press `Ctrl+C` in the terminal running `app.py`
- **Frontend**: Press `Ctrl+C` in the terminal running `npm run dev`

## Next Steps

1. **Search for flights**: Use the main dashboard to search for flights by route and date
2. **View predictions**: See delay risk predictions for each flight
3. **Monthly analysis**: Use the monthly dashboard to analyze airline performance over time
4. **Add more data**: Import additional historical data using the import scripts

## API Endpoints

- **Flight Status**: `GET /flights/status?from=LAX&to=ORD&date=2025-01-15`
- **Monthly Prediction**: `GET /api/airline-performance/predict?year=2025&month=6&airline=DL`
- **Airlines List**: `GET /api/airlines`
- **Available Months**: `GET /api/airline-performance/available-months`

## Support

If you encounter any issues:
1. Check that both backend and frontend are running
2. Verify database is initialized
3. Check browser console for errors
4. Check terminal output for backend errors


