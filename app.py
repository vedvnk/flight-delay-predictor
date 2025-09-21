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
from models import db, Airport, Airline, Aircraft, Flight, FlightStatus, Route, Weather
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
            '/flights/alternatives'
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
            for flight in flights_db:
                # Calculate delay risk category
                delay_prob = flight.delay_probability or 0.3
                if delay_prob < 0.2:
                    delay_risk = "LOW"
                    delay_risk_percentage = f"{int(delay_prob * 100)}%"
                elif delay_prob < 0.4:
                    delay_risk = "MEDIUM"
                    delay_risk_percentage = f"{int(delay_prob * 100)}%"
                else:
                    delay_risk = "HIGH"
                    delay_risk_percentage = f"{int(delay_prob * 100)}%"
                
                flight_data = {
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
                    "seatsAvailable": flight.seats_available or 0,
                    "totalSeats": flight.total_seats,
                    "loadFactor": flight.load_factor,
                    "onTimeProbability": flight.on_time_probability or 0.5,
                    "delayProbability": flight.delay_probability,
                    "delayRisk": delay_risk,
                    "delayRiskPercentage": delay_risk_percentage,
                    "cancellationProbability": flight.cancellation_probability,
                    "basePrice": flight.base_price,
                    "currentPrice": flight.current_price,
                    "currency": flight.currency,
                    "durationMinutes": flight.duration_minutes,
                    "distanceMiles": flight.distance_miles
                }
                flights.append(flight_data)
            
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

@app.route('/flights/alternatives')
def get_flight_alternatives():
    """Get flight alternatives - Database-powered endpoint"""
    flight_number = request.args.get('flightNumber', '')
    
    if not flight_number:
        return jsonify({'error': 'Missing required parameter: flightNumber'}), 400
    
    if not db_initialized:
        return jsonify({'error': 'Database not initialized. Please run init_db.py first.'}), 500
    
    try:
        with app.app_context():
            # Get original flight info
            original_flight = Flight.query.filter_by(flight_number=flight_number).first()
            if not original_flight:
                return jsonify({'alternatives': []})
            
            # Find alternative flights on the same route and date
            time_window_start = original_flight.scheduled_departure - timedelta(hours=3)
            time_window_end = original_flight.scheduled_departure + timedelta(hours=6)
            
            alternatives = Flight.query.filter(
                and_(
                    Flight.flight_number != flight_number,  # Exclude original flight
                    Flight.origin_airport_id == original_flight.origin_airport_id,
                    Flight.destination_airport_id == original_flight.destination_airport_id,
                    Flight.flight_date == original_flight.flight_date,
                    Flight.scheduled_departure >= time_window_start,
                    Flight.scheduled_departure <= time_window_end
                )
            ).options(
                db.joinedload(Flight.airline),
                db.joinedload(Flight.aircraft)
            ).order_by(desc(Flight.on_time_probability)).limit(5).all()
            
            # Convert to API format
            alternatives_list = []
            for alt in alternatives:
                alternative = {
                    "flightNumber": alt.flight_number,
                    "airline": alt.airline.name if alt.airline else "Unknown",
                    "aircraftType": alt.aircraft.type_code if alt.aircraft else "Unknown",
                    "schedDep": alt.scheduled_departure.isoformat() if alt.scheduled_departure else None,
                    "schedArr": alt.scheduled_arrival.isoformat() if alt.scheduled_arrival else None,
                    "from": original_flight.origin_airport.iata_code if original_flight.origin_airport else "Unknown",
                    "to": original_flight.destination_airport.iata_code if original_flight.destination_airport else "Unknown",
                    "seatsLeft": alt.seats_available or 0,
                    "totalSeats": alt.total_seats,
                    "onTimeProbability": alt.on_time_probability or 0.5,
                    "delayProbability": alt.delay_probability,
                    "gate": alt.gate or "TBD",
                    "terminal": alt.terminal or "TBD",
                    "status": alt.status,
                    "delayMinutes": alt.delay_minutes if alt.delay_minutes and alt.delay_minutes > 0 else None,
                    "durationMinutes": alt.duration_minutes,
                    "basePrice": alt.base_price,
                    "currentPrice": alt.current_price,
                    "currency": alt.currency
                }
                alternatives_list.append(alternative)
            
            return jsonify({
                "alternatives": alternatives_list,
                "originalFlight": flight_number,
                "totalAlternatives": len(alternatives_list)
            })
        
    except Exception as e:
        return jsonify({'error': f'Error finding alternatives: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
