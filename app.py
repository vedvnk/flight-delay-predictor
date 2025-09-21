from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import base64
from io import BytesIO
import json
from datetime import datetime, timezone
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

def load_flight_data():
    """Load flight data from CSV file with error handling"""
    try:
        csv_path = os.path.join(os.path.dirname(__file__), 'flights_lax_ord.csv')
        df = pd.read_csv(csv_path)
        
        # Convert datetime strings to datetime objects for better handling
        df['scheduled_departure'] = pd.to_datetime(df['scheduled_departure'])
        df['actual_departure'] = pd.to_datetime(df['actual_departure'])
        df['scheduled_arrival'] = pd.to_datetime(df['scheduled_arrival'])
        df['actual_arrival'] = pd.to_datetime(df['actual_arrival'])
        
        # Add computed columns for compatibility
        df['Origin_Clean'] = df['origin']
        df['Ident'] = df['flight_number']
        df['Airline'] = df['airline']
        df['Type'] = df['aircraft_type']
        
        return df
        
    except FileNotFoundError:
        print("ERROR: flights_lax_ord.csv not found. Please ensure the file exists.")
        return pd.DataFrame()
    except Exception as e:
        print(f"ERROR loading flight data: {e}")
        return pd.DataFrame()

# Load flight data
df = load_flight_data()

# Validate that data was loaded successfully
if df.empty:
    print("WARNING: No flight data loaded. API will have limited functionality.")
else:
    print(f"Successfully loaded {len(df)} flights from CSV")

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

# Add to dataframe if data exists
if not df.empty:
    df['Airline_Delay_Prob'] = df['Airline'].map(airline_delay_prob).fillna(45)
    df['Origin_Delay_Prob'] = df['Origin_Clean'].map(origin_delay_prob).fillna(45)

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
        'message': 'Flight Delay Predictor API',
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
    """Get flight status - Next.js compatible endpoint with robust filtering"""
    from_airport = request.args.get('from', '').upper()
    to_airport = request.args.get('to', '').upper() 
    date = request.args.get('date', '')
    
    if not from_airport or not to_airport or not date:
        return jsonify({'error': 'Missing required parameters: from, to, date'}), 400
    
    try:
        # Parse the requested date
        request_date = datetime.fromisoformat(date.replace('Z', '+00:00')).date()
        
        # Filter flights by route and date
        filtered_flights = df[
            (df['origin'].str.upper() == from_airport) & 
            (df['destination'].str.upper() == to_airport) &
            (df['scheduled_departure'].dt.date == request_date)
        ]
        
        flights = []
        for _, row in filtered_flights.iterrows():
            # Use actual data from CSV
            delay_minutes = row['delay_minutes'] if pd.notna(row['delay_minutes']) and row['delay_minutes'] > 0 else None
            status = row['status'] if pd.notna(row['status']) else "ON_TIME"
            
            flight_data = {
                "flightNumber": row['flight_number'],
                "airline": row['airline'],
                "from": from_airport,
                "to": to_airport,
                "schedDep": row['scheduled_departure'].isoformat() if pd.notna(row['scheduled_departure']) else None,
                "estDep": row['actual_departure'].isoformat() if pd.notna(row['actual_departure']) else None,
                "schedArr": row['scheduled_arrival'].isoformat() if pd.notna(row['scheduled_arrival']) else None,
                "estArr": row['actual_arrival'].isoformat() if pd.notna(row['actual_arrival']) else None,
                "gate": row['gate'] if pd.notna(row['gate']) else "TBD",
                "status": status,
                "delayMinutes": delay_minutes,
                "seatsAvailable": int(row['seats_available']) if pd.notna(row['seats_available']) else 0,
                "onTimeProbability": float(row['on_time_probability']) if pd.notna(row['on_time_probability']) else 0.5
            }
            flights.append(flight_data)
        
        return jsonify({
            "flights": flights,
            "lastUpdated": datetime.now(timezone.utc).isoformat(),
            "totalFlights": len(flights),
            "route": f"{from_airport} → {to_airport}",
            "date": date
        })
        
    except ValueError as e:
        return jsonify({'error': f'Invalid date format: {date}. Use ISO format (YYYY-MM-DD)'}), 400
    except Exception as e:
        return jsonify({'error': f'Error processing request: {str(e)}'}), 500

@app.route('/flights/alternatives')
def get_flight_alternatives():
    """Get flight alternatives - Next.js compatible endpoint with CSV data"""
    flight_number = request.args.get('flightNumber', '')
    
    if not flight_number:
        return jsonify({'error': 'Missing required parameter: flightNumber'}), 400
    
    try:
        # Get original flight info
        original_flight = df[df['flight_number'] == flight_number]
        if original_flight.empty:
            return jsonify({'alternatives': []})
        
        original = original_flight.iloc[0]
        original_departure_time = original['scheduled_departure']
        
        # Find alternative flights on the same route and date
        # Filter for flights departing within 6 hours of the original flight
        time_window_start = original_departure_time - pd.Timedelta(hours=3)
        time_window_end = original_departure_time + pd.Timedelta(hours=6)
        
        alternatives_df = df[
            (df['flight_number'] != flight_number) &  # Exclude original flight
            (df['origin'] == original['origin']) &
            (df['destination'] == original['destination']) &
            (df['scheduled_departure'] >= time_window_start) &
            (df['scheduled_departure'] <= time_window_end)
        ].sort_values('on_time_probability', ascending=False).head(5)  # Top 5 by on-time probability
        
        alternatives = []
        for _, alt in alternatives_df.iterrows():
            alternative = {
                "flightNumber": alt['flight_number'],
                "airline": alt['airline'],
                "schedDep": alt['scheduled_departure'].isoformat() if pd.notna(alt['scheduled_departure']) else None,
                "schedArr": alt['scheduled_arrival'].isoformat() if pd.notna(alt['scheduled_arrival']) else None,
                "from": alt['origin'],
                "to": alt['destination'],
                "seatsLeft": int(alt['seats_available']) if pd.notna(alt['seats_available']) else 0,
                "onTimeProbability": float(alt['on_time_probability']) if pd.notna(alt['on_time_probability']) else 0.5,
                "gate": alt['gate'] if pd.notna(alt['gate']) else "TBD",
                "status": alt['status'] if pd.notna(alt['status']) else "ON_TIME",
                "delayMinutes": int(alt['delay_minutes']) if pd.notna(alt['delay_minutes']) and alt['delay_minutes'] > 0 else None
            }
            alternatives.append(alternative)
        
        return jsonify({
            "alternatives": alternatives,
            "originalFlight": flight_number,
            "totalAlternatives": len(alternatives)
        })
        
    except Exception as e:
        return jsonify({'error': f'Error finding alternatives: {str(e)}'}), 500

if __name__ == '__main__':
    app.run(debug=True, port=8000)
