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

# Delay probability by airline (historical data) - Updated for LAX-ORD route
airline_delay_prob = {
    'American Airlines': 35, 'United Airlines': 42, 'Delta Air Lines': 28, 
    'Alaska Airlines': 31, 'Southwest Airlines': 38, 'JetBlue Airways': 33,
    'Frontier Airlines': 46, 'Spirit Airlines': 52, 'Allegiant Air': 58,
    'Sun Country Airlines': 45
}

# Delay probability by origin airport - LAX specific
origin_delay_prob = {
    'LAX': 47  # Los Angeles International Airport delay probability
}

# Database initialization completed

def predict_flight_delay(flight_id):
    """Enhanced delay prediction using CSV data"""
    try:
        flight = df[df['Ident'] == flight_id].iloc[0]
        
        # Use actual delay data if available, otherwise use probability model
        if pd.notna(flight['delay_minutes']) and flight['delay_minutes'] > 0:
            actual_delay = flight['delay_minutes']
            if actual_delay <= 15:
                risk = "LOW RISK"
                risk_color = "success"
                combined_prob = 25
            elif actual_delay <= 60:
                risk = "MEDIUM RISK"
                risk_color = "warning"
                combined_prob = 45
            else:
                risk = "HIGH RISK"
                risk_color = "danger"
                combined_prob = 75
        else:
            # Use probability model for prediction
            airline_prob = flight['Airline_Delay_Prob']
            origin_prob = flight['Origin_Delay_Prob']
            
            # Factor in on-time probability from CSV
            if 'on_time_probability' in flight and pd.notna(flight['on_time_probability']):
                on_time_prob = flight['on_time_probability']
                combined_prob = ((airline_prob * 0.3) + (origin_prob * 0.3) + ((1 - on_time_prob) * 100 * 0.4))
            else:
                combined_prob = (airline_prob * 0.4) + (origin_prob * 0.6)

            if combined_prob <= 30:
                risk = "LOW RISK"
                risk_color = "success"
            elif combined_prob <= 50:
                risk = "MEDIUM RISK"
                risk_color = "warning"
            else:
                risk = "HIGH RISK"
                risk_color = "danger"

        return {
            'flight_id': flight_id,
            'airline': flight['Airline'],
            'origin': flight['Origin_Clean'],
            'destination': flight.get('destination', 'ORD'),
            'scheduled_departure': flight['scheduled_departure'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(flight['scheduled_departure']) else None,
            'scheduled_arrival': flight['scheduled_arrival'].strftime('%Y-%m-%d %H:%M:%S') if pd.notna(flight['scheduled_arrival']) else None,
            'actual_delay': int(flight.get('delay_minutes', 0)) if pd.notna(flight.get('delay_minutes', 0)) else 0,
            'status': flight.get('status', 'UNKNOWN'),
            'gate': flight.get('gate', 'TBD'),
            'combined_prob': round(combined_prob),
            'airline_prob': int(flight['Airline_Delay_Prob']),
            'origin_prob': int(flight['Origin_Delay_Prob']),
            'risk': risk,
            'risk_color': risk_color
        }
    except (IndexError, KeyError) as e:
        raise IndexError(f"Flight {flight_id} not found or data incomplete")

def plot_to_base64(fig):
    """Convert matplotlib figure to base64 string"""
    img_buffer = BytesIO()
    fig.savefig(img_buffer, format='png', dpi=300, bbox_inches='tight')
    img_buffer.seek(0)
    img_str = base64.b64encode(img_buffer.getvalue()).decode()
    img_buffer.close()
    plt.close(fig)
    return img_str

@app.route('/')
def index():
    """Main page - API status"""
    return jsonify({
        'status': 'running',
        'message': 'OnTime API',
        'version': '1.0.0',
        'endpoints': [
            '/api/flights',
            '/api/predict/<flight_id>',
            '/flights/status',
            '/flights/alternatives'
        ]
    })

@app.route('/api/flights')
def get_flights():
    """Get list of all flights"""
    if df.empty:
        return jsonify({'error': 'No flight data available'}), 503
        
    flights = []
    for _, row in df.iterrows():
        flights.append({
            'id': row['Ident'],
            'display': f"{row['Ident']} - {row['Airline']} from {row['Origin_Clean']}",
            'airline': row['Airline'],
            'origin': row['Origin_Clean'],
            'destination': row.get('destination', 'ORD'),
            'scheduled_departure': row['scheduled_departure'].isoformat() if pd.notna(row['scheduled_departure']) else None,
            'status': row.get('status', 'UNKNOWN')
        })
    return jsonify(flights)

@app.route('/api/predict/<flight_id>')
def predict_delay(flight_id):
    """Get delay prediction for a specific flight"""
    if df.empty:
        return jsonify({'error': 'No flight data available'}), 503
        
    try:
        result = predict_flight_delay(flight_id)
        return jsonify(result)
    except IndexError:
        return jsonify({'error': 'Flight not found'}), 404
    except Exception as e:
        return jsonify({'error': f'Error predicting delay: {str(e)}'}), 500

@app.route('/api/charts/airline')
def get_airline_chart():
    """Get airline delay statistics chart"""
    fig, ax = plt.subplots(figsize=(12, 8))

    airline_stats = df.groupby('Airline')['Airline_Delay_Prob'].first().sort_values()

    colors = ['#28a745' if x <= 30 else '#ffc107' if x <= 50 else '#dc3545' for x in airline_stats.values]

    bars = ax.bar(range(len(airline_stats)), airline_stats.values, color=colors)
    ax.set_title('Delay Probability by Airline', fontsize=16, fontweight='bold')
    ax.set_xlabel('Airline', fontsize=12)
    ax.set_ylabel('Delay Probability (%)', fontsize=12)
    ax.set_xticks(range(len(airline_stats)))
    ax.set_xticklabels(airline_stats.index, rotation=45, ha='right')

    # Add percentage labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                f'{height:.0f}%', ha='center', va='bottom', fontweight='bold')

    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    
    return jsonify({'chart': plot_to_base64(fig)})

@app.route('/api/charts/origin')
def get_origin_chart():
    """Get origin airport delay statistics chart"""
    fig, ax = plt.subplots(figsize=(12, 10))

    origin_stats = df.groupby('Origin_Clean')['Origin_Delay_Prob'].first().sort_values()

    # Truncate long airport names for display
    display_names = []
    for name in origin_stats.index:
        if len(name) > 25:
            display_names.append(name[:22] + "...")
        else:
            display_names.append(name)

    colors = ['#28a745' if x <= 30 else '#ffc107' if x <= 50 else '#dc3545' for x in origin_stats.values]

    bars = ax.barh(range(len(origin_stats)), origin_stats.values, color=colors)
    ax.set_title('Delay Probability by Origin Airport', fontsize=14, fontweight='bold')
    ax.set_xlabel('Delay Probability (%)', fontsize=12)
    ax.set_ylabel('Origin Airport', fontsize=10)
    ax.set_yticks(range(len(origin_stats)))
    ax.set_yticklabels(display_names, fontsize=9)

    # Add percentage labels
    for i, bar in enumerate(bars):
        width = bar.get_width()
        ax.text(width + 1, bar.get_y() + bar.get_height()/2.,
                f'{width:.0f}%', ha='left', va='center', fontweight='bold', fontsize=9)

    ax.grid(axis='x', alpha=0.3)
    ax.set_xlim(0, max(origin_stats.values) + 10)
    plt.tight_layout()
    
    return jsonify({'chart': plot_to_base64(fig)})

@app.route('/api/charts/combined')
def get_combined_chart():
    """Get overall delay probability distribution chart"""
    fig, ax = plt.subplots(figsize=(10, 6))

    # Calculate combined probability for each flight
    df['Combined_Prob'] = (df['Airline_Delay_Prob'] * 0.4) + (df['Origin_Delay_Prob'] * 0.6)

    # Create bins
    bins = [0, 30, 50, 100]
    labels = ['Low Risk\n(≤30%)', 'Medium Risk\n(31-50%)', 'High Risk\n(>50%)']
    colors = ['#28a745', '#ffc107', '#dc3545']

    counts = []
    for i in range(len(bins)-1):
        count = len(df[(df['Combined_Prob'] > bins[i]) & (df['Combined_Prob'] <= bins[i+1])])
        counts.append(count)

    bars = ax.bar(labels, counts, color=colors)
    ax.set_title('Flight Delay Risk Distribution', fontsize=16, fontweight='bold')
    ax.set_ylabel('Number of Flights', fontsize=12)

    # Add count labels
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                f'{int(height)}', ha='center', va='bottom', fontweight='bold', fontsize=14)

    plt.tight_layout()
    
    return jsonify({'chart': plot_to_base64(fig)})

# Next.js compatible endpoints
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
