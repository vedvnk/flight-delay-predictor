#!/usr/bin/env python3
"""
Train Machine Learning Models for Flight Delay Prediction
=========================================================

This script trains ML models using the flight data from the database
and saves them for use in the API.
"""

import os
import sys
import pandas as pd
from datetime import datetime
from ml_predictor import FlightDelayPredictor, generate_synthetic_flight_data

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from app import app
from models import db, Flight, Airport, Airline, Aircraft

def load_flight_data_from_db():
    """Load flight data from the database for training."""
    print("📊 Loading flight data from database...")
    
    with app.app_context():
        # Query flights with related data
        flights = Flight.query.options(
            db.joinedload(Flight.airline),
            db.joinedload(Flight.aircraft),
            db.joinedload(Flight.origin_airport),
            db.joinedload(Flight.destination_airport)
        ).all()
        
        if not flights:
            print("❌ No flights found in database")
            return pd.DataFrame()
        
        # Convert to DataFrame
        flight_data = []
        for flight in flights:
            data = {
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
                'delay_probability': flight.delay_probability,
                'cancellation_probability': flight.cancellation_probability,
                'duration_minutes': flight.duration_minutes,
                'distance_miles': flight.distance_miles,
                'flight_date': flight.flight_date
            }
            flight_data.append(data)
        
        df = pd.DataFrame(flight_data)
        print(f"✅ Loaded {len(df)} flights from database")
        return df

def main():
    """Main training function."""
    print("🤖 Flight Delay ML Model Training")
    print("=" * 50)
    
    # Load data from database
    db_data = load_flight_data_from_db()
    
    if len(db_data) < 10:
        print("⚠️  Insufficient data in database. Generating synthetic data for training...")
        training_data = generate_synthetic_flight_data(2000)
        print(f"✅ Generated {len(training_data)} synthetic flights")
    else:
        print(f"📊 Using {len(db_data)} flights from database")
        # Combine with synthetic data for better training
        synthetic_data = generate_synthetic_flight_data(1000)
        training_data = pd.concat([db_data, synthetic_data], ignore_index=True)
        print(f"✅ Combined with {len(synthetic_data)} synthetic flights = {len(training_data)} total")
    
    # Initialize predictor
    predictor = FlightDelayPredictor()
    
    # Train models
    print("\n🚀 Training ML models...")
    results = predictor.train_models(training_data)
    
    # Store training results
    predictor.training_results = results
    
    # Display results
    print("\n📈 Model Performance Summary:")
    print("-" * 40)
    for name, result in results.items():
        if 'error' not in result:
            print(f"{name:20} | R² = {result['test_r2']:.3f} | RMSE = {np.sqrt(result['test_mse']):.1f}")
        else:
            print(f"{name:20} | Error: {result['error']}")
    
    # Save models
    print(f"\n💾 Saving trained models...")
    predictor.save_models()
    
    # Test prediction on a sample flight
    print(f"\n🔮 Testing prediction on sample flight...")
    sample_flight = training_data.iloc[0].to_dict()
    
    try:
        prediction = predictor.predict_delay(sample_flight)
        print(f"   Flight: {sample_flight['flight_number']}")
        print(f"   Route: {sample_flight['origin']} → {sample_flight['destination']}")
        print(f"   Predicted Delay: {prediction['predicted_delay_minutes']:.1f} minutes")
        print(f"   Risk Level: {prediction['prediction_quality']}")
        print(f"   Model Used: {prediction['model_used']}")
        print(f"   Confidence: ±{prediction['confidence_interval']:.1f} minutes")
    except Exception as e:
        print(f"   ❌ Prediction test failed: {str(e)}")
    
    print(f"\n✅ Training complete! Models saved to 'models/' directory")
    print(f"📊 Best model: {predictor.best_model}")
    print(f"🎯 Ready for production use in API endpoints")

if __name__ == "__main__":
    import numpy as np
    main()
