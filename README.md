# OnTime

A full-stack application for predicting flight delays with real-time data and beautiful glassmorphic UI design.

![OnTime](https://img.shields.io/badge/Status-Active-green)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Next.js](https://img.shields.io/badge/Next.js-15.0-black)
![Flask](https://img.shields.io/badge/Flask-Latest-red)

## 🚀 Features

### Backend (Flask API)
- **Real Flight Data**: 24+ flights from LAX to ORD with actual delay information
- **Delay Prediction**: Advanced algorithms using airline and airport statistics
- **RESTful API**: Clean endpoints for flight status and alternatives
- **CORS Enabled**: Seamless frontend integration
- **CSV Data Source**: Real flight data with schedules, delays, and probabilities

### Frontend (Next.js)
- **Modern UI**: Glassmorphic design with smooth animations
- **Real-time Search**: Auto-loading flight data on page visit
- **Responsive Design**: Works perfectly on desktop and mobile
- **Flight Alternatives**: Compare alternative flights with delay probabilities
- **React Query**: Efficient data fetching with caching
- **TypeScript**: Full type safety with Zod validation

## 🏗️ Architecture

```
flight-delay-predictor/
├── app.py                 # Flask backend server
├── flights_lax_ord.csv   # Real flight data
├── requirements.txt      # Python dependencies
└── frontend/             # Next.js application
    ├── src/
    │   ├── app/          # Next.js app router
    │   ├── components/   # React components
    │   ├── hooks/        # React Query hooks
    │   └── lib/          # Utilities and API client
    └── package.json      # Node.js dependencies
```

## 🚦 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm or yarn

### 1. Clone the Repository
```bash
git clone https://github.com/Aadi077/flight-delay-predictor.git
cd flight-delay-predictor
```

### 2. Start the Backend
```bash
# Install Python dependencies
pip install -r requirements.txt

# Start Flask server
python3 app.py
```
Backend will be available at `http://localhost:8000`

### 3. Start the Frontend
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000 npm run dev
```
Frontend will be available at `http://localhost:3000`

## 📊 API Endpoints

### Flight Status
```http
GET /flights/status?from=LAX&to=ORD&date=2025-09-21
```

**Response:**
```json
{
  "flights": [
    {
      "flightNumber": "AA1247",
      "airline": "American Airlines",
      "from": "LAX",
      "to": "ORD",
      "schedDep": "2025-09-21T06:00:00-07:00",
      "estDep": "2025-09-21T06:15:00-07:00",
      "status": "DELAYED",
      "delayMinutes": 15,
      "gate": "B12",
      "onTimeProbability": 0.72
    }
  ],
  "totalFlights": 24,
  "lastUpdated": "2025-09-21T05:13:57.275242+00:00"
}
```

### Flight Alternatives
```http
GET /flights/alternatives?flightNumber=AA1247
```

**Response:**
```json
{
  "alternatives": [
    {
      "flightNumber": "UA342",
      "airline": "United Airlines",
      "schedDep": "2025-09-21T07:15:00-07:00",
      "schedArr": "2025-09-21T12:45:00-05:00",
      "seatsLeft": 45,
      "onTimeProbability": 0.85
    }
  ],
  "totalAlternatives": 5
}
```

## 🎨 Screenshots

### Main Dashboard
- Clean search interface with LAX→ORD default
- Real-time flight data loading
- Glassmorphic design elements

### Flight Results
- 24 real flights with actual delay information
- Color-coded status indicators
- Delay predictions and gate information

### Flight Alternatives
- Alternative flight suggestions
- On-time probability comparisons
- Seat availability information

## 🛠️ Technical Details

### Backend Stack
- **Flask**: Python web framework
- **Pandas**: Data manipulation and analysis
- **Flask-CORS**: Cross-origin resource sharing
- **CSV Data**: Real flight information storage

### Frontend Stack
- **Next.js 15**: React framework with App Router
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **React Query**: Data fetching and caching
- **Zod**: Runtime type validation
- **Framer Motion**: Smooth animations

### Data Source
The application uses real flight data from `flights_lax_ord.csv` containing:
- 24 flights from LAX to ORD
- Actual departure/arrival times
- Delay information and status
- Gate assignments and seat availability
- On-time probability calculations

## 🔧 Development

### Backend Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run with debug mode
python3 app.py
```

### Frontend Development
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Run tests
npm test

# Build for production
npm run build
```

## 🌐 Deployment

### Backend Deployment
- Deploy Flask app to Heroku, Railway, or similar
- Update CORS settings for production domain
- Configure environment variables

### Frontend Deployment
- Deploy to Vercel, Netlify, or similar
- Set `NEXT_PUBLIC_API_BASE_URL` to production API URL
- Configure build settings

## 📈 Performance Features

- **React Query Caching**: Efficient data fetching with 30-second stale time
- **Automatic Retries**: Robust error handling with exponential backoff
- **Optimistic Updates**: Smooth user experience
- **Responsive Design**: Mobile-first approach
- **Loading States**: Skeleton screens and loading indicators

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- Real flight data for LAX→ORD route
- Modern glassmorphic design inspiration
- React Query for excellent data management
- Next.js team for the amazing framework

## 📞 Support

If you have any questions or need help with the project, please:
- Open an issue on GitHub
- Check the documentation
- Review the API endpoints

---

**Live Demo**: Visit the application at `http://localhost:3000` after following the setup instructions.

**Backend API**: Explore the API at `http://localhost:8000` with endpoints documented above.