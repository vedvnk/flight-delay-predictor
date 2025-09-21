"""
Machine Learning Flight Delay Predictor
=======================================

This module implements linear regression models for predicting flight delays
using various features extracted from flight data.
"""

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import joblib
import os
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

class FlightDelayPredictor:
    """
    Machine Learning model for predicting flight delays using multiple algorithms.
    """
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.models = {}
        self.scalers = {}
        self.label_encoders = {}
        self.feature_columns = []
        self.target_column = 'delay_minutes'
        
        # Create models directory
        os.makedirs(model_dir, exist_ok=True)
        
        # Initialize models
        self._initialize_models()
        
    def _initialize_models(self):
        """Initialize different ML models for delay prediction."""
        self.models = {
            'linear_regression': LinearRegression(),
            'ridge_regression': Ridge(alpha=1.0),
            'lasso_regression': Lasso(alpha=0.1),
            'random_forest': RandomForestRegressor(n_estimators=100, random_state=42)
        }
        
    def extract_features(self, flights_df: pd.DataFrame) -> pd.DataFrame:
        """
        Extract and engineer features from flight data for ML training.
        
        Args:
            flights_df: DataFrame containing flight data
            
        Returns:
            DataFrame with engineered features
        """
        df = flights_df.copy()
        
        # Convert datetime columns
        datetime_cols = ['scheduled_departure', 'actual_departure', 'scheduled_arrival', 'actual_arrival']
        for col in datetime_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Time-based features
        if 'scheduled_departure' in df.columns:
            df['departure_hour'] = df['scheduled_departure'].dt.hour
            df['departure_minute'] = df['scheduled_departure'].dt.minute
            df['departure_day_of_week'] = df['scheduled_departure'].dt.dayofweek
            df['departure_month'] = df['scheduled_departure'].dt.month
            df['departure_is_weekend'] = (df['departure_day_of_week'] >= 5).astype(int)
            
            # Peak hours (6-9 AM, 5-8 PM)
            df['departure_is_peak'] = (
                ((df['departure_hour'] >= 6) & (df['departure_hour'] <= 9)) |
                ((df['departure_hour'] >= 17) & (df['departure_hour'] <= 20))
            ).astype(int)
            
            # Early morning (4-6 AM) and late night (10 PM - 4 AM)
            df['departure_is_off_peak'] = (
                ((df['departure_hour'] >= 4) & (df['departure_hour'] <= 6)) |
                (df['departure_hour'] >= 22) | (df['departure_hour'] <= 4)
            ).astype(int)
        
        # Flight duration features
        if 'scheduled_departure' in df.columns and 'scheduled_arrival' in df.columns:
            df['scheduled_duration_minutes'] = (
                df['scheduled_arrival'] - df['scheduled_departure']
            ).dt.total_seconds() / 60
        
        # Aircraft type features (encoded)
        if 'aircraft_type' in df.columns:
            le_aircraft = LabelEncoder()
            df['aircraft_type_encoded'] = le_aircraft.fit_transform(df['aircraft_type'].astype(str))
            self.label_encoders['aircraft_type'] = le_aircraft
        
        # Airline features (encoded)
        if 'airline' in df.columns:
            le_airline = LabelEncoder()
            df['airline_encoded'] = le_airline.fit_transform(df['airline'].astype(str))
            self.label_encoders['airline'] = le_airline
        
        # Airport features (encoded)
        if 'origin' in df.columns:
            le_origin = LabelEncoder()
            df['origin_encoded'] = le_origin.fit_transform(df['origin'].astype(str))
            self.label_encoders['origin'] = le_origin
            
        if 'destination' in df.columns:
            le_destination = LabelEncoder()
            df['destination_encoded'] = le_destination.fit_transform(df['destination'].astype(str))
            self.label_encoders['destination'] = le_destination
        
        # Route complexity (number of flights on same route)
        if 'origin' in df.columns and 'destination' in df.columns:
            route_counts = df.groupby(['origin', 'destination']).size()
            df['route_frequency'] = df.apply(
                lambda x: route_counts.get((x['origin'], x['destination']), 1), axis=1
            )
        
        # Historical delay patterns by airline
        if 'airline' in df.columns and 'delay_minutes' in df.columns:
            airline_delays = df.groupby('airline')['delay_minutes'].agg(['mean', 'std']).fillna(0)
            df = df.merge(
                airline_delays, 
                left_on='airline', 
                right_index=True, 
                how='left',
                suffixes=('', '_airline_hist')
            )
            df['airline_avg_delay'] = df['mean'].fillna(0)
            df['airline_delay_std'] = df['std'].fillna(0)
            df.drop(['mean', 'std'], axis=1, inplace=True)
        
        # Historical delay patterns by route
        if 'origin' in df.columns and 'destination' in df.columns and 'delay_minutes' in df.columns:
            route_delays = df.groupby(['origin', 'destination'])['delay_minutes'].agg(['mean', 'std']).fillna(0)
            df = df.merge(
                route_delays,
                left_on=['origin', 'destination'],
                right_index=True,
                how='left',
                suffixes=('', '_route_hist')
            )
            df['route_avg_delay'] = df['mean'].fillna(0)
            df['route_delay_std'] = df['std'].fillna(0)
            df.drop(['mean', 'std'], axis=1, inplace=True)
        
        # Seat capacity features
        if 'seats_available' in df.columns and 'total_seats' in df.columns:
            df['load_factor'] = 1 - (df['seats_available'] / df['total_seats'].replace(0, 1))
        elif 'seats_available' in df.columns:
            # Estimate load factor based on seats available
            df['estimated_load_factor'] = np.clip(1 - (df['seats_available'] / 200), 0, 1)
        
        # Gate features (terminal congestion proxy)
        if 'gate' in df.columns:
            df['gate_number'] = df['gate'].str.extract(r'(\d+)').astype(float)
            df['terminal'] = df['gate'].str.extract(r'([A-Z]+)')
            if 'terminal' in df.columns:
                le_terminal = LabelEncoder()
                df['terminal_encoded'] = le_terminal.fit_transform(df['terminal'].fillna('Unknown').astype(str))
                self.label_encoders['terminal'] = le_terminal
        
        return df
    
    def prepare_training_data(self, flights_df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.Series]:
        """
        Prepare training data with features and target variable.
        
        Args:
            flights_df: Raw flight data
            
        Returns:
            Tuple of (features_df, target_series)
        """
        # Extract features
        df = self.extract_features(flights_df)
        
        # Define feature columns
        feature_cols = [
            'departure_hour', 'departure_minute', 'departure_day_of_week', 'departure_month',
            'departure_is_weekend', 'departure_is_peak', 'departure_is_off_peak',
            'scheduled_duration_minutes', 'aircraft_type_encoded', 'airline_encoded',
            'origin_encoded', 'destination_encoded', 'route_frequency',
            'airline_avg_delay', 'airline_delay_std', 'route_avg_delay', 'route_delay_std'
        ]
        
        # Add optional features if they exist
        optional_features = ['load_factor', 'estimated_load_factor', 'gate_number', 'terminal_encoded']
        for col in optional_features:
            if col in df.columns:
                feature_cols.append(col)
        
        # Filter to existing columns
        feature_cols = [col for col in feature_cols if col in df.columns]
        
        # Prepare features and target
        X = df[feature_cols].fillna(0)
        y = df[self.target_column].fillna(0)
        
        # Store feature columns for later use
        self.feature_columns = feature_cols
        
        return X, y
    
    def train_models(self, flights_df: pd.DataFrame) -> Dict[str, Dict]:
        """
        Train all ML models on flight data.
        
        Args:
            flights_df: Training data
            
        Returns:
            Dictionary with training results for each model
        """
        print("🔄 Preparing training data...")
        X, y = self.prepare_training_data(flights_df)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        self.scalers['standard'] = scaler
        
        results = {}
        
        print("🚀 Training models...")
        for name, model in self.models.items():
            print(f"   Training {name}...")
            
            try:
                # Train model
                model.fit(X_train_scaled, y_train)
                
                # Make predictions
                y_pred_train = model.predict(X_train_scaled)
                y_pred_test = model.predict(X_test_scaled)
                
                # Calculate metrics
                train_mse = mean_squared_error(y_train, y_pred_train)
                test_mse = mean_squared_error(y_test, y_pred_test)
                train_r2 = r2_score(y_train, y_pred_train)
                test_r2 = r2_score(y_test, y_pred_test)
                train_mae = mean_absolute_error(y_train, y_pred_train)
                test_mae = mean_absolute_error(y_test, y_pred_test)
                
                # Cross-validation score
                cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='neg_mean_squared_error')
                cv_rmse = np.sqrt(-cv_scores.mean())
                
                results[name] = {
                    'model': model,
                    'train_mse': train_mse,
                    'test_mse': test_mse,
                    'train_r2': train_r2,
                    'test_r2': test_r2,
                    'train_mae': train_mae,
                    'test_mae': test_mae,
                    'cv_rmse': cv_rmse,
                    'feature_importance': getattr(model, 'feature_importances_', None)
                }
                
                print(f"   ✅ {name}: R² = {test_r2:.3f}, RMSE = {np.sqrt(test_mse):.1f}")
                
            except Exception as e:
                print(f"   ❌ {name}: Error - {str(e)}")
                results[name] = {'error': str(e)}
        
        # Save the best model
        best_model_name = max(
            [name for name, result in results.items() if 'error' not in result],
            key=lambda x: results[x]['test_r2']
        )
        
        print(f"🏆 Best model: {best_model_name}")
        self.best_model = best_model_name
        
        return results
    
    def predict_delay(self, flight_data: Dict) -> Dict[str, float]:
        """
        Predict delay for a single flight using the best trained model.
        
        Args:
            flight_data: Dictionary containing flight information
            
        Returns:
            Dictionary with prediction results
        """
        if not hasattr(self, 'best_model') or not self.best_model or self.best_model not in self.models:
            # Try to use any available model if best_model is not set
            available_models = [name for name, model in self.models.items() if model is not None]
            if not available_models:
                raise ValueError("No trained model available. Train models first.")
            self.best_model = available_models[0]
            print(f"Using {self.best_model} as default model")
        
        # Convert to DataFrame for feature extraction
        df = pd.DataFrame([flight_data])
        X, _ = self.prepare_training_data(df)
        
        # Ensure all required features are present
        for col in self.feature_columns:
            if col not in X.columns:
                X[col] = 0
        
        X = X[self.feature_columns].fillna(0)
        
        # Scale features
        if 'standard' in self.scalers:
            X_scaled = self.scalers['standard'].transform(X)
        else:
            X_scaled = X.values
        
        # Make prediction
        model = self.models[self.best_model]
        predicted_delay = model.predict(X_scaled)[0]
        
        # Get confidence interval (approximate)
        if hasattr(self, 'training_results') and self.training_results:
            std_error = np.sqrt(self.training_results.get(self.best_model, {}).get('test_mse', 100))
        else:
            # Default confidence interval if no training results available
            std_error = 10.0
        confidence_interval = 1.96 * std_error  # 95% confidence
        
        return {
            'predicted_delay_minutes': max(0, predicted_delay),
            'confidence_interval': confidence_interval,
            'model_used': self.best_model,
            'prediction_quality': self._get_prediction_quality(predicted_delay)
        }
    
    def _get_prediction_quality(self, predicted_delay: float) -> str:
        """Determine prediction quality based on delay magnitude."""
        if predicted_delay <= 15:
            return "LOW_RISK"
        elif predicted_delay <= 60:
            return "MEDIUM_RISK"
        else:
            return "HIGH_RISK"
    
    def save_models(self, filename_prefix: str = "flight_delay_models"):
        """Save trained models and preprocessors."""
        for name, model in self.models.items():
            model_path = os.path.join(self.model_dir, f"{filename_prefix}_{name}.joblib")
            joblib.dump(model, model_path)
        
        # Save scalers and encoders
        joblib.dump(self.scalers, os.path.join(self.model_dir, f"{filename_prefix}_scalers.joblib"))
        joblib.dump(self.label_encoders, os.path.join(self.model_dir, f"{filename_prefix}_encoders.joblib"))
        joblib.dump(self.feature_columns, os.path.join(self.model_dir, f"{filename_prefix}_features.joblib"))
        
        print(f"💾 Models saved to {self.model_dir}/")
    
    def load_models(self, filename_prefix: str = "flight_delay_models"):
        """Load previously trained models and preprocessors."""
        try:
            # Load models
            for name in self.models.keys():
                model_path = os.path.join(self.model_dir, f"{filename_prefix}_{name}.joblib")
                if os.path.exists(model_path):
                    self.models[name] = joblib.load(model_path)
            
            # Load scalers and encoders
            scalers_path = os.path.join(self.model_dir, f"{filename_prefix}_scalers.joblib")
            encoders_path = os.path.join(self.model_dir, f"{filename_prefix}_encoders.joblib")
            features_path = os.path.join(self.model_dir, f"{filename_prefix}_features.joblib")
            
            if os.path.exists(scalers_path):
                self.scalers = joblib.load(scalers_path)
            if os.path.exists(encoders_path):
                self.label_encoders = joblib.load(encoders_path)
            if os.path.exists(features_path):
                self.feature_columns = joblib.load(features_path)
            
            # Set best model to the first available model
            available_models = [name for name, model in self.models.items() if model is not None]
            if available_models:
                self.best_model = available_models[0]
                print(f"✅ Models loaded successfully. Using {self.best_model} as default model")
            else:
                print("⚠️  Models loaded but no valid models found")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Error loading models: {str(e)}")
            return False
    
    def get_model_performance(self) -> Dict:
        """Get performance metrics for all trained models."""
        if not hasattr(self, 'training_results'):
            return {}
        
        performance = {}
        for name, result in self.training_results.items():
            if 'error' not in result:
                performance[name] = {
                    'r2_score': result['test_r2'],
                    'rmse': np.sqrt(result['test_mse']),
                    'mae': result['test_mae'],
                    'cv_rmse': result['cv_rmse']
                }
        
        return performance

def generate_synthetic_flight_data(n_flights: int = 1000) -> pd.DataFrame:
    """
    Generate synthetic flight data for training ML models.
    
    Args:
        n_flights: Number of synthetic flights to generate
        
    Returns:
        DataFrame with synthetic flight data
    """
    np.random.seed(42)
    
    airlines = ['American Airlines', 'United Airlines', 'Delta Air Lines', 'Southwest Airlines', 'Alaska Airlines']
    aircraft_types = ['Boeing 737-800', 'Boeing 737-900', 'Airbus A320', 'Boeing 777-200', 'Boeing 757-200']
    airports = ['LAX', 'ORD', 'JFK', 'ATL', 'DFW', 'DEN', 'SFO', 'SEA']
    gates = [f"{terminal}{num}" for terminal in ['A', 'B', 'C', 'D', 'E'] for num in range(1, 21)]
    
    data = []
    base_time = datetime(2024, 1, 1, 6, 0, 0)
    
    for i in range(n_flights):
        # Basic flight info
        airline = np.random.choice(airlines)
        aircraft = np.random.choice(aircraft_types)
        origin = np.random.choice(airports)
        destination = np.random.choice([a for a in airports if a != origin])
        gate = np.random.choice(gates)
        
        # Time features - probability distribution for departure hours
        hour_probs = [
            0.02, 0.02, 0.02, 0.02, 0.05, 0.08, 0.12, 0.10, 0.08, 0.06, 0.05, 0.05,
            0.05, 0.06, 0.08, 0.10, 0.12, 0.08, 0.05, 0.03, 0.02, 0.02, 0.02, 0.02
        ]
        # Normalize probabilities to sum to 1
        hour_probs = np.array(hour_probs) / np.sum(hour_probs)
        departure_hour = int(np.random.choice(range(24), p=hour_probs))
        departure_minute = np.random.randint(0, 60)
        
        scheduled_departure = base_time + timedelta(
            days=i // 20,
            hours=departure_hour,
            minutes=departure_minute
        )
        
        # Flight duration (2-6 hours)
        duration_minutes = np.random.normal(240, 60)
        duration_minutes = max(120, min(360, duration_minutes))
        
        scheduled_arrival = scheduled_departure + timedelta(minutes=duration_minutes)
        
        # Delay factors
        delay_base = 0
        
        # Airline-specific delays
        airline_delays = {
            'American Airlines': 0.3,
            'United Airlines': 0.4,
            'Delta Air Lines': 0.25,
            'Southwest Airlines': 0.35,
            'Alaska Airlines': 0.2
        }
        delay_base += airline_delays[airline] * 20
        
        # Time-based delays
        if departure_hour in range(6, 10) or departure_hour in range(17, 21):  # Peak hours
            delay_base += 15
        elif departure_hour in range(22, 24) or departure_hour in range(0, 6):  # Off-peak
            delay_base += 5
        
        # Day of week delays
        day_of_week = scheduled_departure.weekday()
        if day_of_week >= 5:  # Weekend
            delay_base += 10
        
        # Route-specific delays
        busy_routes = [('LAX', 'JFK'), ('ORD', 'LAX'), ('ATL', 'LAX')]
        if (origin, destination) in busy_routes:
            delay_base += 20
        
        # Random component
        delay_minutes = max(0, np.random.exponential(delay_base))
        
        # Cap extreme delays
        delay_minutes = min(delay_minutes, 300)
        
        # Calculate actual times
        actual_departure = scheduled_departure + timedelta(minutes=delay_minutes)
        actual_arrival = scheduled_arrival + timedelta(minutes=delay_minutes)
        
        # Status
        if delay_minutes <= 15:
            status = 'ON_TIME'
        elif delay_minutes <= 60:
            status = 'DELAYED'
        else:
            status = 'DELAYED'
        
        # Seats
        total_seats = np.random.choice([150, 180, 189, 215, 440])
        seats_available = np.random.randint(0, total_seats // 4)
        
        # On-time probability (inverse of delay risk)
        on_time_prob = max(0.1, 1 - (delay_minutes / 120))
        
        flight_data = {
            'flight_number': f"{airline[:2].upper()}{np.random.randint(1000, 9999)}",
            'airline': airline,
            'aircraft_type': aircraft,
            'origin': origin,
            'destination': destination,
            'scheduled_departure': scheduled_departure,
            'actual_departure': actual_departure,
            'scheduled_arrival': scheduled_arrival,
            'actual_arrival': actual_arrival,
            'gate': gate,
            'status': status,
            'delay_minutes': delay_minutes,
            'seats_available': seats_available,
            'total_seats': total_seats,
            'on_time_probability': on_time_prob
        }
        
        data.append(flight_data)
    
    return pd.DataFrame(data)

if __name__ == "__main__":
    # Example usage
    print("🤖 Flight Delay ML Predictor")
    print("=" * 40)
    
    # Generate synthetic data
    print("📊 Generating synthetic training data...")
    training_data = generate_synthetic_flight_data(2000)
    print(f"✅ Generated {len(training_data)} flights")
    
    # Initialize predictor
    predictor = FlightDelayPredictor()
    
    # Train models
    results = predictor.train_models(training_data)
    
    # Save models
    predictor.save_models()
    
    # Test prediction
    sample_flight = training_data.iloc[0].to_dict()
    prediction = predictor.predict_delay(sample_flight)
    
    print(f"\n🔮 Sample Prediction:")
    print(f"   Flight: {sample_flight['flight_number']}")
    print(f"   Route: {sample_flight['origin']} → {sample_flight['destination']}")
    print(f"   Predicted Delay: {prediction['predicted_delay_minutes']:.1f} minutes")
    print(f"   Risk Level: {prediction['prediction_quality']}")
    print(f"   Model Used: {prediction['model_used']}")
