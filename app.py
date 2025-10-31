from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_, or_, desc, func
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import base64
from io import BytesIO
import json
from datetime import datetime, timezone, timedelta
import os
from models import db, Airport, Airline, Aircraft, Flight, FlightStatus, Route, Weather, AirlineMonthlyPerformance
from ml_predictor import FlightDelayPredictor

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ontime.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

def init_database():
    """Initialize database connection and create tables if needed"""
    try:
        with app.app_context():
            # Check if database exists and has data
            flight_count = Flight.query.count()
            if flight_count == 0:
                print("⚠️  Database is empty. Run 'python init_db.py' to populate it.")
                return False
            else:
                print(f"✅ Database connected successfully with {flight_count} flights")
                return True
    except Exception as e:
        print(f"❌ Database initialization error: {e}")
        return False

# Initialize database
db_initialized = init_database()

# Initialize ML predictor
ml_predictor = None
ml_models_loaded = False

def init_ml_predictor():
    """Initialize ML predictor and load models."""
    global ml_predictor, ml_models_loaded
    try:
        ml_predictor = FlightDelayPredictor()
        ml_models_loaded = ml_predictor.load_models()
        if ml_models_loaded:
            print(f"✅ ML models loaded successfully. Best model: {getattr(ml_predictor, 'best_model', 'unknown')}")
        else:
            print("⚠️  ML models not found. Run 'python train_ml_models.py' to train models.")
        return ml_models_loaded
    except Exception as e:
        print(f"❌ Error initializing ML predictor: {e}")
        ml_models_loaded = False
        return False

# Initialize ML predictor
init_ml_predictor()

@app.route('/')
def index():
    """Main page - API status"""
    return jsonify({
        'status': 'running',
        'message': 'OnTime API',
        'version': '1.0.0',
        'database_initialized': db_initialized,
        'ml_models_loaded': ml_models_loaded,
        'endpoints': [
            '/api/flights',
            '/api/predict/<flight_id>',
            '/api/predict/ml/<flight_id>',
            '/api/models/performance',
            '/flights/status',
            '/flights/delay-analysis',
            '/api/airlines',
            '/api/airline-performance/monthly',
            '/api/airline-performance/predict',
            '/api/airline-performance/available-months'
        ]
    })

@app.route('/api/flights')
def get_flights():
    """Get list of all flights - Database powered"""
    if not db_initialized:
        return jsonify({'error': 'Database not initialized. Please run init_db.py first.'}), 500
    
    try:
        with app.app_context():
            flights = Flight.query.options(
                db.joinedload(Flight.airline),
                db.joinedload(Flight.aircraft),
                db.joinedload(Flight.origin_airport),
                db.joinedload(Flight.destination_airport)
            ).all()
            
            flights_list = [flight.to_dict() for flight in flights]
            return jsonify({'flights': flights_list})
    except Exception as e:
        return jsonify({'error': f'Failed to fetch flights: {str(e)}'}), 500

@app.route('/api/predict/<flight_id>')
def predict_delay(flight_id):
    """Get delay prediction for a specific flight - Database powered"""
    if not db_initialized:
        return jsonify({'error': 'Database not initialized. Please run init_db.py first.'}), 500
        
    try:
        with app.app_context():
            flight = Flight.query.filter_by(flight_number=flight_id).first()
            if not flight:
                return jsonify({'error': 'Flight not found'}), 404
            
            prediction = {
                'flight_number': flight.flight_number,
                'airline': flight.airline.name if flight.airline else 'Unknown',
                'on_time_probability': flight.on_time_probability or 0.5,
                'delay_probability': flight.delay_probability or 0.3,
                'cancellation_probability': flight.cancellation_probability or 0.05,
                'predicted_delay_minutes': flight.delay_minutes or 0,
                'status': flight.status
            }
            return jsonify(prediction)
    except Exception as e:
        return jsonify({'error': f'Failed to predict delay: {str(e)}'}), 500

@app.route('/api/predict/ml/<flight_id>')
def predict_delay_ml(flight_id):
    """Get ML-powered delay prediction for a specific flight"""
    if not db_initialized:
        return jsonify({'error': 'Database not initialized. Please run init_db.py first.'}), 500
    
    if not ml_models_loaded:
        return jsonify({'error': 'ML models not loaded. Please run train_ml_models.py first.'}), 500
        
    try:
        with app.app_context():
            flight = Flight.query.filter_by(flight_number=flight_id).first()
            if not flight:
                return jsonify({'error': 'Flight not found'}), 404
            
            # Prepare flight data for ML prediction
            flight_data = {
                'flight_number': flight.flight_number,
                'airline': flight.airline.name if flight.airline else 'Unknown',
                'aircraft_type': flight.aircraft.type_code if flight.aircraft else 'Unknown',
                'origin': flight.origin_airport.iata_code if flight.origin_airport else 'Unknown',
                'destination': flight.destination_airport.iata_code if flight.destination_airport else 'Unknown',
                'scheduled_departure': flight.scheduled_departure,
                'actual_departure': flight.actual_departure,
                'scheduled_arrival': flight.scheduled_arrival,
                'actual_arrival': flight.actual_arrival,
                'gate': flight.gate,
                'terminal': flight.terminal,
                'status': flight.status,
                'delay_minutes': flight.delay_minutes or 0,
                'seats_available': flight.seats_available,
                'total_seats': flight.total_seats,
                'on_time_probability': flight.on_time_probability,
                'duration_minutes': flight.duration_minutes,
                'distance_miles': flight.distance_miles,
                'flight_date': flight.flight_date
            }
            
            # Get ML prediction
            ml_prediction = ml_predictor.predict_delay(flight_data)
            
            # Combine with database prediction
            prediction = {
                'flight_number': flight.flight_number,
                'airline': flight.airline.name if flight.airline else 'Unknown',
                'route': f"{flight.origin_airport.iata_code if flight.origin_airport else 'Unknown'} → {flight.destination_airport.iata_code if flight.destination_airport else 'Unknown'}",
                'scheduled_departure': flight.scheduled_departure.isoformat() if flight.scheduled_departure else None,
                'current_status': flight.status,
                'actual_delay_minutes': flight.delay_minutes or 0,
                
                # ML Predictions
                'ml_predicted_delay_minutes': ml_prediction['predicted_delay_minutes'],
                'ml_confidence_interval': ml_prediction['confidence_interval'],
                'ml_prediction_quality': ml_prediction['prediction_quality'],
                'ml_model_used': ml_prediction['model_used'],
                
                # Database Predictions (for comparison)
                'db_on_time_probability': flight.on_time_probability or 0.5,
                'db_delay_probability': flight.delay_probability or 0.3,
                'db_cancellation_probability': flight.cancellation_probability or 0.05,
                
                # Combined Analysis
                'recommendation': _get_flight_recommendation(ml_prediction, flight),
                'risk_factors': _analyze_risk_factors(flight_data)
            }
            
            return jsonify(prediction)
            
    except Exception as e:
        return jsonify({'error': f'Failed to predict delay with ML: {str(e)}'}), 500

@app.route('/api/models/performance')
def get_model_performance():
    """Get performance metrics for all trained ML models"""
    if not ml_models_loaded:
        return jsonify({'error': 'ML models not loaded. Please run train_ml_models.py first.'}), 500
    
    try:
        performance = ml_predictor.get_model_performance()
        return jsonify({
            'models': performance,
            'best_model': getattr(ml_predictor, 'best_model', 'unknown'),
            'feature_count': len(ml_predictor.feature_columns) if hasattr(ml_predictor, 'feature_columns') else 0,
            'feature_columns': ml_predictor.feature_columns if hasattr(ml_predictor, 'feature_columns') else []
        })
    except Exception as e:
        return jsonify({'error': f'Failed to get model performance: {str(e)}'}), 500

def _get_flight_recommendation(ml_prediction: dict, flight: Flight) -> str:
    """Generate flight recommendation based on ML prediction and flight data."""
    predicted_delay = ml_prediction['predicted_delay_minutes']
    risk_level = ml_prediction['prediction_quality']
    
    if risk_level == 'LOW_RISK':
        return "RECOMMENDED - Low delay risk"
    elif risk_level == 'MEDIUM_RISK':
        if flight.seats_available and flight.seats_available > 50:
            return "CONDITIONAL - Medium delay risk, but good availability"
        else:
            return "CAUTION - Medium delay risk with limited seats"
    else:  # HIGH_RISK
        return "NOT RECOMMENDED - High delay risk"

def _analyze_risk_factors(flight_data: dict) -> list:
    """Analyze risk factors for a flight."""
    risk_factors = []
    
    # Time-based risks
    if flight_data.get('scheduled_departure'):
        departure_time = flight_data['scheduled_departure']
        if hasattr(departure_time, 'hour'):
            hour = departure_time.hour
            if hour in range(6, 10) or hour in range(17, 21):
                risk_factors.append("Peak hour departure")
            elif hour in range(22, 24) or hour in range(0, 6):
                risk_factors.append("Off-peak departure")
    
    # Airline risks
    airline = flight_data.get('airline', '')
    high_delay_airlines = ['United Airlines', 'American Airlines']
    if airline in high_delay_airlines:
        risk_factors.append("Airline with higher delay rates")
    
    # Route risks
    origin = flight_data.get('origin', '')
    destination = flight_data.get('destination', '')
    busy_routes = [('LAX', 'JFK'), ('ORD', 'LAX'), ('ATL', 'LAX')]
    if (origin, destination) in busy_routes:
        risk_factors.append("Busy route with higher congestion")
    
    # Capacity risks
    if flight_data.get('seats_available', 0) < 20:
        risk_factors.append("Limited seat availability")
    
    if not risk_factors:
        risk_factors.append("No significant risk factors identified")
    
    return risk_factors

@app.route('/flights/status')
def get_flight_status():
    """Get flight status - Database-powered endpoint with comprehensive data"""
    from_airport = request.args.get('from', '').upper()
    to_airport = request.args.get('to', '').upper() 
    date = request.args.get('date', '')
    
    if not from_airport or not to_airport or not date:
        return jsonify({'error': 'Missing required parameters: from, to, date'}), 400
    
    if not db_initialized:
        return jsonify({'error': 'Database not initialized. Please run init_db.py first.'}), 500
    
    try:
        # Parse the requested date
        try:
            request_date = datetime.strptime(date, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        with app.app_context():
            # Get airports
            origin_airport = Airport.query.filter_by(iata_code=from_airport).first()
            destination_airport = Airport.query.filter_by(iata_code=to_airport).first()
            
            if not origin_airport or not destination_airport:
                return jsonify({
                    'flights': [],
                    'lastUpdated': datetime.now(timezone.utc).isoformat(),
                    'message': f'Airport not found: {from_airport} or {to_airport}'
                })
            
            # Query flights from database
            flights_query = Flight.query.filter(
                and_(
                    Flight.origin_airport_id == origin_airport.id,
                    Flight.destination_airport_id == destination_airport.id,
                    Flight.flight_date == request_date
                )
            ).options(
                db.joinedload(Flight.airline),
                db.joinedload(Flight.aircraft),
                db.joinedload(Flight.origin_airport),
                db.joinedload(Flight.destination_airport)
            ).order_by(Flight.scheduled_departure)
            
            flights_db = flights_query.all()
            
            if not flights_db:
                return jsonify({
                    'flights': [],
                    'lastUpdated': datetime.now(timezone.utc).isoformat(),
                    'message': f'No flights found for {from_airport} to {to_airport} on {date}'
                })
            
            # Convert to API format
            flights = []
            import random
            weather_conditions = ['clear', 'cloudy', 'rain', 'storm', 'fog']
            for flight in flights_db:
                # Simulate weather and NAS features
                flight_weather = random.choice(weather_conditions)
                flight_nas_congestion = round(random.uniform(0.3, 0.95), 2)
                airport_congestion = round(random.uniform(0.3, 0.98), 2)
                # TODO: Use real weather/NAS/congestion API here instead of random values
                # Prepare ML feature dict for per-flight prediction
                flight_data = {
                    'flight_number': flight.flight_number,
                    'airline': flight.airline.name if flight.airline else 'Unknown',
                    'aircraft_type': flight.aircraft.type_code if flight.aircraft else 'Unknown',
                    'origin': from_airport,
                    'destination': to_airport,
                    'scheduled_departure': flight.scheduled_departure,
                    'actual_departure': flight.actual_departure,
                    'scheduled_arrival': flight.scheduled_arrival,
                    'actual_arrival': flight.actual_arrival,
                    'gate': flight.gate,
                    'terminal': flight.terminal,
                    'status': flight.status,
                    'seats_available': flight.seats_available,
                    'total_seats': flight.total_seats,
                    'route_frequency': flight.route_frequency,
                    # Simulated and historic features
                    'weather_condition': flight_weather,
                    'current_nas_congestion': flight_nas_congestion,
                    'current_airport_congestion': airport_congestion
                }
                try:
                    ml_prediction = ml_predictor.predict_delay(flight_data)
                    delay_minutes_pred = ml_prediction['predicted_delay_minutes']
                    delay_probability = min(max(delay_minutes_pred/60, 0), 1)  # Assume 60+ mins ~ 1.0 risk
                    delay_risk = ml_prediction['prediction_quality'].replace('_RISK', '')
                except Exception as e:
                    delay_probability = 0.2
                    delay_minutes_pred = 5
                    delay_risk = 'LOW'
                # Convert to API format as before, but using the new prediction fields:
                flights.append({
                    "flightNumber": flight.flight_number,
                    "airline": flight.airline.name if flight.airline else "Unknown",
                    "aircraftType": flight.aircraft.type_code if flight.aircraft else "Unknown",
                    "from": from_airport,
                    "to": to_airport,
                    "schedDep": flight.scheduled_departure.isoformat() if flight.scheduled_departure else None,
                    "estDep": flight.actual_departure.isoformat() if flight.actual_departure else None,
                    "schedArr": flight.scheduled_arrival.isoformat() if flight.scheduled_arrival else None,
                    "estArr": flight.actual_arrival.isoformat() if flight.actual_arrival else None,
                    "gate": flight.gate or "TBD",
                    "terminal": flight.terminal or "TBD",
                    "status": flight.status,
                    "delayMinutes": flight.delay_minutes if flight.delay_minutes and flight.delay_minutes > 0 else None,
                    "delayPercentage": flight.delay_percentage,
                    "seatsAvailable": flight.seats_available or 0,
                    "totalSeats": flight.total_seats,
                    # Add prediction fields:
                    "delayProbability": delay_probability,
                    "predictedDelayMinutes": delay_minutes_pred,
                    "delayRisk": delay_risk,
                })
            
            return jsonify({
                "flights": flights,
                "lastUpdated": datetime.now(timezone.utc).isoformat(),
                "totalFlights": len(flights),
                "route": f"{from_airport} → {to_airport}",
                "date": date,
                "originAirport": origin_airport.to_dict(),
                "destinationAirport": destination_airport.to_dict()
            })
        
    except Exception as e:
        return jsonify({'error': f'Failed to fetch flights: {str(e)}'}), 500

@app.route('/flights/delay-analysis')
def get_delay_analysis():
    """Get comprehensive delay analysis for flights"""
    from_airport = request.args.get('from', '').upper()
    to_airport = request.args.get('to', '').upper()
    
    if not from_airport or not to_airport:
        return jsonify({'error': 'Missing required parameters: from, to'}), 400
    
    if not db_initialized:
        return jsonify({'error': 'Database not initialized. Please run init_db.py first.'}), 500
    
    try:
        with app.app_context():
            # Get origin and destination airports
            origin_airport = Airport.query.filter_by(iata_code=from_airport).first()
            destination_airport = Airport.query.filter_by(iata_code=to_airport).first()
            
            if not origin_airport or not destination_airport:
                return jsonify({'error': f'Airport not found: {from_airport} or {to_airport}'}), 404
            
            # Get flights for analysis
            flights = Flight.query.filter(
                and_(
                    Flight.origin_airport_id == origin_airport.id,
                    Flight.destination_airport_id == destination_airport.id,
                    Flight.primary_delay_reason.isnot(None)
                )
            ).options(
                db.joinedload(Flight.airline),
                db.joinedload(Flight.aircraft)
            ).all()
            
            if not flights:
                return jsonify({
                    'delay_analysis': {
                        'total_flights': 0,
                        'delayed_flights': 0,
                        'delay_percentage': 0,
                        'primary_reasons': {},
                        'average_delay_minutes': 0,
                        'confidence_score': 0
                    }
                })
            
            # Analyze delay patterns
            delay_reasons = {}
            total_delays = 0
            total_delay_minutes = 0
            confidence_scores = []
            
            for flight in flights:
                if flight.delay_minutes and flight.delay_minutes > 0:
                    total_delays += 1
                    total_delay_minutes += flight.delay_minutes
                    
                    reason = flight.primary_delay_reason
                    if reason:
                        delay_reasons[reason] = delay_reasons.get(reason, 0) + 1
                    
                    if flight.delay_reason_confidence:
                        confidence_scores.append(flight.delay_reason_confidence)
            
            # Calculate statistics
            total_flights = len(flights)
            delay_percentage = (total_delays / total_flights) * 100 if total_flights > 0 else 0
            average_delay_minutes = total_delay_minutes / total_delays if total_delays > 0 else 0
            average_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            # Convert counts to percentages
            reason_percentages = {}
            for reason, count in delay_reasons.items():
                reason_percentages[reason] = (count / total_delays) * 100 if total_delays > 0 else 0
            
            return jsonify({
                'delay_analysis': {
                    'total_flights': total_flights,
                    'delayed_flights': total_delays,
                    'delay_percentage': round(delay_percentage, 1),
                    'primary_reasons': reason_percentages,
                    'average_delay_minutes': round(average_delay_minutes, 1),
                    'confidence_score': round(average_confidence, 2),
                    'route': f"{from_airport} → {to_airport}",
                    'last_updated': datetime.now(timezone.utc).isoformat()
                }
            })
        
    except Exception as e:
        return jsonify({'error': f'Error analyzing delays: {str(e)}'}), 500

@app.route('/api/airline-performance/monthly')
def get_monthly_airline_performance():
    """Get monthly airline performance statistics"""
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    airline_code = request.args.get('airline', '').upper()
    
    if not year or not month:
        return jsonify({'error': 'Missing required parameters: year, month'}), 400
    
    if not db_initialized:
        return jsonify({'error': 'Database not initialized. Please run init_db.py first.'}), 500
    
    try:
        with app.app_context():
            # Build query
            query = AirlineMonthlyPerformance.query.filter(
                AirlineMonthlyPerformance.year == year,
                AirlineMonthlyPerformance.month == month
            )
            
            # Filter by airline if specified
            if airline_code:
                airline = Airline.query.filter_by(iata_code=airline_code).first()
                if airline:
                    query = query.filter(AirlineMonthlyPerformance.airline_id == airline.id)
            
            performances = query.options(
                db.joinedload(AirlineMonthlyPerformance.airline),
                db.joinedload(AirlineMonthlyPerformance.airport)
            ).all()
            
            if not performances:
                return jsonify({
                    'performances': [],
                    'message': f'No data found for {year}-{month:02d}' + (f' (airline: {airline_code})' if airline_code else '')
                })
            
            performances_list = [perf.to_dict() for perf in performances]
            
            return jsonify({
                'performances': performances_list,
                'year': year,
                'month': month,
                'total_records': len(performances_list)
            })
            
    except Exception as e:
        return jsonify({'error': f'Failed to fetch performance data: {str(e)}'}), 500

@app.route('/api/airline-performance/predict')
def predict_monthly_delay():
    """Get performance metrics for a given airline and month based on historical data"""
    year = request.args.get('year', type=int)
    month = request.args.get('month', type=int)
    airline_code = request.args.get('airline', '').upper()
    
    if not year or not month or not airline_code:
        return jsonify({'error': 'Missing required parameters: year, month, airline'}), 400
    
    if not db_initialized:
        return jsonify({'error': 'Database not initialized. Please run init_db.py first.'}), 500
    
    try:
        with app.app_context():
            # Get airline
            airline = Airline.query.filter_by(iata_code=airline_code).first()
            if not airline:
                return jsonify({'error': f'Airline not found: {airline_code}'}), 404
            
            # Determine if this is historical or future data
            # Historical data cutoff: Before 2026
            is_historical = year < 2026
            
            # First, try to get actual data for the requested month
            actual_data = AirlineMonthlyPerformance.query.filter(
                AirlineMonthlyPerformance.airline_id == airline.id,
                AirlineMonthlyPerformance.year == year,
                AirlineMonthlyPerformance.month == month
            ).first()
            
            if actual_data and is_historical:
                # Return actual data if available and it's historical
                delay_probability = 100 - (actual_data.on_time_percentage or 0)
                delay_risk_category = "LOW" if delay_probability < 15 else ("MEDIUM" if delay_probability < 30 else "HIGH")
                delay_risk_color = "green" if delay_probability < 15 else ("yellow" if delay_probability < 30 else "red")
                
                avg_delay_minutes = (actual_data.total_delay_minutes or 0) / (actual_data.total_arrivals or 1)
                delay_duration_category = "LOW" if avg_delay_minutes < 30 else ("MEDIUM" if avg_delay_minutes < 60 else "HIGH")
                
                return jsonify({
                    'airline': {
                        'code': airline.iata_code,
                        'name': airline.name
                    },
                    'year': year,
                    'month': month,
                    'data_type': 'actual',
                    'prediction': {
                        'delay_probability': round(delay_probability, 1),
                        'delay_risk_category': delay_risk_category,
                        'delay_risk_color': delay_risk_color,
                        'predicted_delay_duration_minutes': round(avg_delay_minutes, 1),
                        'predicted_delay_duration_formatted': f"{int(avg_delay_minutes)} min",
                        'delay_duration_category': delay_duration_category
                    },
                    'metrics': {
                        'estimated_completion_factor': actual_data.completion_factor,
                        'estimated_cancellation_rate': (actual_data.cancellations or 0) / (actual_data.total_arrivals or 1) * 100,
                        'on_time_percentage': actual_data.on_time_percentage
                    },
                    'delay_causes': [
                        {'cause': 'National Air System', 'percentage': round((actual_data.nas_delay_minutes or 0) / (actual_data.total_delay_minutes or 1) * 100, 1), 'color': '#3b82f6'},
                        {'cause': 'Carrier', 'percentage': round((actual_data.carrier_delay_minutes or 0) / (actual_data.total_delay_minutes or 1) * 100, 1), 'color': '#ef4444'},
                        {'cause': 'Late Aircraft', 'percentage': round((actual_data.late_aircraft_delay_minutes or 0) / (actual_data.total_delay_minutes or 1) * 100, 1), 'color': '#f59e0b'},
                        {'cause': 'Weather', 'percentage': round((actual_data.weather_delay_minutes or 0) / (actual_data.total_delay_minutes or 1) * 100, 1), 'color': '#10b981'},
                        {'cause': 'Security', 'percentage': round((actual_data.security_delay_minutes or 0) / (actual_data.total_delay_minutes or 1) * 100, 1), 'color': '#8b5cf6'}
                    ],
                    'historical_basis': {
                        'months_analyzed': 1,
                        'latest_data': {
                            'year': actual_data.year,
                            'month': actual_data.month,
                            'on_time_percentage': actual_data.on_time_percentage,
                            'completion_factor': actual_data.completion_factor
                        }
                    }
                })
            
            # Get historical performance data for prediction
            historical_data = AirlineMonthlyPerformance.query.filter(
                AirlineMonthlyPerformance.airline_id == airline.id
            ).order_by(
                AirlineMonthlyPerformance.year.desc(),
                AirlineMonthlyPerformance.month.desc()
            ).limit(12).all()
            
            if not historical_data:
                return jsonify({'error': f'No historical data found for airline: {airline_code}'}), 404
            
            # Get most recent data as baseline
            latest = historical_data[0]
            
            # Calculate predictions based on historical trends
            # Simple approach: use recent average
            avg_delay_rate = sum(1 - (perf.on_time_percentage or 0) / 100 for perf in historical_data) / len(historical_data)
            avg_delay_minutes = sum((perf.total_delay_minutes or 0) / (perf.total_arrivals or 1) for perf in historical_data) / len(historical_data)
            
            # Predict delay probability
            delay_probability = avg_delay_rate * 100
            
            # Categorize delay risk
            if delay_probability < 15:
                delay_risk_category = "LOW"
                delay_risk_color = "green"
            elif delay_probability < 30:
                delay_risk_category = "MEDIUM"
                delay_risk_color = "yellow"
            else:
                delay_risk_category = "HIGH"
                delay_risk_color = "red"
            
            # Predict delay duration based on historical average
            predicted_delay_duration = avg_delay_minutes
            
            # Categorize delay duration
            if predicted_delay_duration < 30:
                delay_duration_category = "LOW"
            elif predicted_delay_duration < 60:
                delay_duration_category = "MEDIUM"
            else:
                delay_duration_category = "HIGH"
            
            # Calculate delay causes distribution from historical data
            total_carrier = sum(perf.carrier_delay_minutes or 0 for perf in historical_data)
            total_weather = sum(perf.weather_delay_minutes or 0 for perf in historical_data)
            total_nas = sum(perf.nas_delay_minutes or 0 for perf in historical_data)
            total_late_aircraft = sum(perf.late_aircraft_delay_minutes or 0 for perf in historical_data)
            total_security = sum(perf.security_delay_minutes or 0 for perf in historical_data)
            
            total_all = total_carrier + total_weather + total_nas + total_late_aircraft + total_security
            
            delay_causes = []
            if total_all > 0:
                delay_causes = [
                    {'cause': 'National Air System', 'percentage': round((total_nas / total_all) * 100, 1), 'color': '#3b82f6'},
                    {'cause': 'Carrier', 'percentage': round((total_carrier / total_all) * 100, 1), 'color': '#ef4444'},
                    {'cause': 'Late Aircraft', 'percentage': round((total_late_aircraft / total_all) * 100, 1), 'color': '#f59e0b'},
                    {'cause': 'Weather', 'percentage': round((total_weather / total_all) * 100, 1), 'color': '#10b981'},
                    {'cause': 'Security', 'percentage': round((total_security / total_all) * 100, 1), 'color': '#8b5cf6'}
                ]
                # Sort by percentage descending
                delay_causes.sort(key=lambda x: x['percentage'], reverse=True)
            
            # Additional metrics
            avg_completion_factor = sum(perf.completion_factor or 0 for perf in historical_data) / len(historical_data)
            avg_cancellation_rate = sum((perf.cancellations or 0) / (perf.total_arrivals or 1) * 100 for perf in historical_data) / len(historical_data)
            
            prediction = {
                'airline': {
                    'code': airline.iata_code,
                    'name': airline.name
                },
                'year': year,
                'month': month,
                'data_type': 'predicted',
                'prediction': {
                    'delay_probability': round(delay_probability, 1),
                    'delay_risk_category': delay_risk_category,
                    'delay_risk_color': delay_risk_color,
                    'predicted_delay_duration_minutes': round(predicted_delay_duration, 1),
                    'predicted_delay_duration_formatted': f"{int(predicted_delay_duration)} min",
                    'delay_duration_category': delay_duration_category
                },
                'metrics': {
                    'estimated_completion_factor': round(avg_completion_factor, 2),
                    'estimated_cancellation_rate': round(avg_cancellation_rate, 2),
                    'on_time_percentage': round(100 - delay_probability, 2)
                },
                'delay_causes': delay_causes,
                'historical_basis': {
                    'months_analyzed': len(historical_data),
                    'latest_data': {
                        'year': latest.year,
                        'month': latest.month,
                        'on_time_percentage': latest.on_time_percentage,
                        'completion_factor': latest.completion_factor
                    }
                }
            }
            
            return jsonify(prediction)
            
    except Exception as e:
        return jsonify({'error': f'Failed to generate prediction: {str(e)}'}), 500

@app.route('/api/airlines')
def get_airlines():
    """Get list of all airlines with performance data"""
    if not db_initialized:
        return jsonify({'error': 'Database not initialized. Please run init_db.py first.'}), 500
    
    try:
        with app.app_context():
            # Get airlines that have performance data
            airlines_with_data = db.session.query(Airline).join(
                AirlineMonthlyPerformance
            ).distinct().all()
            
            airlines_list = [airline.to_dict() for airline in airlines_with_data]
            
            return jsonify({
                'airlines': airlines_list,
                'total': len(airlines_list)
            })
            
    except Exception as e:
        return jsonify({'error': f'Failed to fetch airlines: {str(e)}'}), 500

@app.route('/api/airline-performance/available-months')
def get_available_months():
    """Get list of available year-month combinations"""
    if not db_initialized:
        return jsonify({'error': 'Database not initialized. Please run init_db.py first.'}), 500
    
    try:
        with app.app_context():
            periods = db.session.query(
                AirlineMonthlyPerformance.year,
                AirlineMonthlyPerformance.month
            ).distinct().order_by(
                AirlineMonthlyPerformance.year.desc(),
                AirlineMonthlyPerformance.month.desc()
            ).all()
            
            periods_list = [
                {
                    'year': year,
                    'month': month,
                    'label': f"{year}-{month:02d}",
                    'month_name': datetime(year, month, 1).strftime('%B %Y')
                }
                for year, month in periods
            ]
            
            return jsonify({
                'periods': periods_list,
                'total': len(periods_list)
            })
            
    except Exception as e:
        return jsonify({'error': f'Failed to fetch available months: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
