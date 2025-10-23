#!/usr/bin/env python3
"""
Real Data Integration for Flight Delay Predictor
==============================================

This module integrates real-time weather data and flight information
from various APIs and data sources.
"""

import requests
import json
import os
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
import time
from dataclasses import dataclass

@dataclass
class WeatherData:
    """Weather data structure"""
    airport_code: str
    temperature_celsius: float
    humidity_percent: float
    wind_speed_mph: float
    wind_direction_degrees: float
    visibility_miles: float
    precipitation_inches: float
    conditions: str
    delay_factor: float
    cancellation_risk: float
    timestamp: datetime

@dataclass
class FlightData:
    """Flight data structure"""
    flight_number: str
    airline: str
    origin: str
    destination: str
    scheduled_departure: datetime
    actual_departure: Optional[datetime]
    scheduled_arrival: datetime
    actual_arrival: Optional[datetime]
    status: str
    delay_minutes: int
    gate: Optional[str]
    terminal: Optional[str]
    aircraft_type: str
    seats_available: Optional[int]
    total_seats: Optional[int]

class RealWeatherAPI:
    """Real weather data integration using OpenWeatherMap API"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        
    def get_weather_by_coordinates(self, lat: float, lon: float, airport_code: str) -> Optional[WeatherData]:
        """Get real weather data by coordinates"""
        if not self.api_key:
            print("⚠️  OpenWeatherMap API key not found. Using fallback weather data.")
            return self._get_fallback_weather(airport_code)
        
        try:
            url = f"{self.base_url}/weather"
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract weather information
            main = data.get('main', {})
            weather = data.get('weather', [{}])[0]
            wind = data.get('wind', {})
            visibility = data.get('visibility', 10000) / 1000  # Convert to miles
            
            temperature = main.get('temp', 20)
            humidity = main.get('humidity', 50)
            wind_speed = wind.get('speed', 0) * 2.237  # Convert m/s to mph
            wind_direction = wind.get('deg', 0)
            conditions = weather.get('main', 'CLEAR').upper()
            
            # Calculate precipitation (simplified - would need more detailed API)
            precipitation = 0
            if conditions in ['RAIN', 'DRIZZLE']:
                precipitation = 0.1
            elif conditions == 'THUNDERSTORM':
                precipitation = 0.3
            
            # Calculate delay factors based on real weather conditions
            delay_factor = self._calculate_delay_factor(conditions, wind_speed, visibility)
            cancellation_risk = self._calculate_cancellation_risk(conditions, wind_speed)
            
            return WeatherData(
                airport_code=airport_code,
                temperature_celsius=temperature,
                humidity_percent=humidity,
                wind_speed_mph=wind_speed,
                wind_direction_degrees=wind_direction,
                visibility_miles=visibility,
                precipitation_inches=precipitation,
                conditions=conditions,
                delay_factor=delay_factor,
                cancellation_risk=cancellation_risk,
                timestamp=datetime.now()
            )
            
        except Exception as e:
            print(f"❌ Error fetching weather data for {airport_code}: {e}")
            return self._get_fallback_weather(airport_code)
    
    def _calculate_delay_factor(self, conditions: str, wind_speed: float, visibility: float) -> float:
        """Calculate delay factor based on weather conditions"""
        delay_factor = 1.0
        
        # Weather condition delays
        if conditions == 'THUNDERSTORM':
            delay_factor *= 1.8
        elif conditions in ['RAIN', 'DRIZZLE']:
            delay_factor *= 1.3
        elif conditions in ['SNOW', 'SLEET']:
            delay_factor *= 1.6
        elif conditions == 'FOG':
            delay_factor *= 1.4
        
        # Wind speed delays
        if wind_speed > 25:
            delay_factor *= 1.4
        elif wind_speed > 20:
            delay_factor *= 1.2
        elif wind_speed > 15:
            delay_factor *= 1.1
        
        # Visibility delays
        if visibility < 1:
            delay_factor *= 1.5
        elif visibility < 3:
            delay_factor *= 1.3
        elif visibility < 5:
            delay_factor *= 1.1
        
        return min(delay_factor, 3.0)  # Cap at 3x delay
    
    def _calculate_cancellation_risk(self, conditions: str, wind_speed: float) -> float:
        """Calculate cancellation risk based on weather conditions"""
        if conditions == 'THUNDERSTORM' and wind_speed > 30:
            return 0.15
        elif conditions in ['SNOW', 'SLEET'] and wind_speed > 25:
            return 0.10
        elif conditions == 'THUNDERSTORM':
            return 0.05
        else:
            return 0.01
    
    def _get_fallback_weather(self, airport_code: str) -> WeatherData:
        """Fallback weather data when API is unavailable"""
        return WeatherData(
            airport_code=airport_code,
            temperature_celsius=20,
            humidity_percent=60,
            wind_speed_mph=10,
            wind_direction_degrees=180,
            visibility_miles=10,
            precipitation_inches=0,
            conditions='CLEAR',
            delay_factor=1.0,
            cancellation_risk=0.01,
            timestamp=datetime.now()
        )

class RealFlightDataAPI:
    """Real flight data integration using FlightAware API"""
    
    def __init__(self):
        self.api_key = os.getenv('FLIGHTAWARE_API_KEY')
        self.username = os.getenv('FLIGHTAWARE_USERNAME')
        self.base_url = "http://flightxml.flightaware.com/json/FlightXML3"
        
    def get_flights_by_airport(self, airport_code: str, hours_ahead: int = 6) -> List[FlightData]:
        """Get real flights for an airport"""
        if not self.api_key or not self.username:
            print("⚠️  FlightAware API credentials not found. Using fallback flight data.")
            return self._get_fallback_flights(airport_code)
        
        try:
            # FlightAware API call for airport flights
            url = f"{self.base_url}/AirportBoards"
            params = {
                'airport_code': airport_code,
                'include_ex_data': 'true',
                'type': 'departures',
                'howMany': 50,
                'offset': 0
            }
            
            auth = (self.username, self.api_key)
            response = requests.get(url, params=params, auth=auth, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            flights = []
            
            if 'AirportBoardsResult' in data and 'departures' in data['AirportBoardsResult']:
                for flight_info in data['AirportBoardsResult']['departures']:
                    flight_data = self._parse_flight_info(flight_info)
                    if flight_data:
                        flights.append(flight_data)
            
            return flights
            
        except Exception as e:
            print(f"❌ Error fetching flight data for {airport_code}: {e}")
            return self._get_fallback_flights(airport_code)
    
    def _parse_flight_info(self, flight_info: Dict) -> Optional[FlightData]:
        """Parse FlightAware flight information"""
        try:
            flight_number = flight_info.get('ident', '')
            airline = flight_info.get('airline', 'Unknown')
            origin = flight_info.get('origin', {}).get('code', '')
            destination = flight_info.get('destination', {}).get('code', '')
            
            # Parse times
            scheduled_departure = self._parse_time(flight_info.get('scheduled_out'))
            actual_departure = self._parse_time(flight_info.get('estimated_out'))
            scheduled_arrival = self._parse_time(flight_info.get('scheduled_in'))
            actual_arrival = self._parse_time(flight_info.get('estimated_in'))
            
            status = flight_info.get('status', 'ON_TIME')
            gate = flight_info.get('gate', None)
            terminal = flight_info.get('terminal', None)
            aircraft_type = flight_info.get('aircrafttype', 'Unknown')
            
            # Calculate delay
            delay_minutes = 0
            if scheduled_departure and actual_departure:
                delay_minutes = int((actual_departure - scheduled_departure).total_seconds() / 60)
            
            return FlightData(
                flight_number=flight_number,
                airline=airline,
                origin=origin,
                destination=destination,
                scheduled_departure=scheduled_departure or datetime.now(),
                actual_departure=actual_departure,
                scheduled_arrival=scheduled_arrival or datetime.now(),
                actual_arrival=actual_arrival,
                status=status,
                delay_minutes=delay_minutes,
                gate=gate,
                terminal=terminal,
                aircraft_type=aircraft_type,
                seats_available=None,
                total_seats=None
            )
            
        except Exception as e:
            print(f"❌ Error parsing flight info: {e}")
            return None
    
    def _parse_time(self, time_str: Optional[str]) -> Optional[datetime]:
        """Parse time string to datetime"""
        if not time_str:
            return None
        try:
            # FlightAware time format: "2024-01-01T12:00:00Z"
            return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        except:
            return None
    
    def _get_fallback_flights(self, airport_code: str) -> List[FlightData]:
        """Fallback flight data when API is unavailable"""
        # Return empty list - we'll use other methods to get real data
        return []

class AviationStackAPI:
    """Alternative flight data source using AviationStack API"""
    
    def __init__(self):
        self.api_key = os.getenv('AVIATIONSTACK_API_KEY')
        self.base_url = "http://api.aviationstack.com/v1"
        
    def get_live_flights(self, airport_code: str) -> List[FlightData]:
        """Get live flights using AviationStack API"""
        if not self.api_key:
            print("⚠️  AviationStack API key not found.")
            return []
        
        try:
            url = f"{self.base_url}/flights"
            params = {
                'access_key': self.api_key,
                'dep_iata': airport_code,
                'flight_status': 'active'
            }
            
            response = requests.get(url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            flights = []
            
            if 'data' in data:
                for flight_info in data['data']:
                    flight_data = self._parse_aviation_stack_flight(flight_info)
                    if flight_data:
                        flights.append(flight_data)
            
            return flights
            
        except Exception as e:
            print(f"❌ Error fetching AviationStack data: {e}")
            return []
    
    def _parse_aviation_stack_flight(self, flight_info: Dict) -> Optional[FlightData]:
        """Parse AviationStack flight information"""
        try:
            flight_data = flight_info.get('flight', {})
            departure = flight_info.get('departure', {})
            arrival = flight_info.get('arrival', {})
            
            flight_number = flight_data.get('number', '')
            airline = flight_data.get('airline', {}).get('name', 'Unknown')
            origin = departure.get('iata', '')
            destination = arrival.get('iata', '')
            
            # Parse times
            scheduled_departure = self._parse_aviation_time(departure.get('scheduled'))
            actual_departure = self._parse_aviation_time(departure.get('actual'))
            scheduled_arrival = self._parse_aviation_time(arrival.get('scheduled'))
            actual_arrival = self._parse_aviation_time(arrival.get('actual'))
            
            status = flight_info.get('flight_status', 'ON_TIME')
            gate = departure.get('gate', None)
            terminal = departure.get('terminal', None)
            aircraft_type = flight_info.get('aircraft', {}).get('iata', 'Unknown')
            
            # Calculate delay
            delay_minutes = 0
            if scheduled_departure and actual_departure:
                delay_minutes = int((actual_departure - scheduled_departure).total_seconds() / 60)
            
            return FlightData(
                flight_number=flight_number,
                airline=airline,
                origin=origin,
                destination=destination,
                scheduled_departure=scheduled_departure or datetime.now(),
                actual_departure=actual_departure,
                scheduled_arrival=scheduled_arrival or datetime.now(),
                actual_arrival=actual_arrival,
                status=status,
                delay_minutes=delay_minutes,
                gate=gate,
                terminal=terminal,
                aircraft_type=aircraft_type,
                seats_available=None,
                total_seats=None
            )
            
        except Exception as e:
            print(f"❌ Error parsing AviationStack flight: {e}")
            return None
    
    def _parse_aviation_time(self, time_str: Optional[str]) -> Optional[datetime]:
        """Parse AviationStack time format"""
        if not time_str:
            return None
        try:
            # AviationStack format: "2024-01-01T12:00:00+00:00"
            return datetime.fromisoformat(time_str.replace('+00:00', ''))
        except:
            return None

class RealDataIntegrator:
    """Main class to integrate real weather and flight data"""
    
    def __init__(self):
        self.weather_api = RealWeatherAPI()
        self.flight_api = RealFlightDataAPI()
        self.aviation_api = AviationStackAPI()
        
    def get_real_weather_for_airport(self, airport_code: str, lat: float, lon: float) -> Optional[WeatherData]:
        """Get real weather data for an airport"""
        return self.weather_api.get_weather_by_coordinates(lat, lon, airport_code)
    
    def get_real_flights_for_airport(self, airport_code: str) -> List[FlightData]:
        """Get real flights for an airport using multiple sources"""
        flights = []
        
        # Try FlightAware first
        try:
            flights.extend(self.flight_api.get_flights_by_airport(airport_code))
        except Exception as e:
            print(f"❌ FlightAware failed: {e}")
        
        # Try AviationStack as backup
        try:
            flights.extend(self.aviation_api.get_live_flights(airport_code))
        except Exception as e:
            print(f"❌ AviationStack failed: {e}")
        
        # Remove duplicates based on flight number
        unique_flights = {}
        for flight in flights:
            if flight.flight_number not in unique_flights:
                unique_flights[flight.flight_number] = flight
        
        return list(unique_flights.values())
    
    def update_database_with_real_data(self):
        """Update database with real weather and flight data"""
        from app import app
        from models import db, Airport, Flight, Weather, Airline, Aircraft
        
        with app.app_context():
            # Get all airports
            airports = Airport.query.all()
            
            print("🌤️  Fetching real weather data...")
            weather_count = 0
            
            for airport in airports:
                try:
                    weather_data = self.get_real_weather_for_airport(
                        airport.iata_code, 
                        airport.latitude, 
                        airport.longitude
                    )
                    
                    if weather_data:
                        # Store weather data
                        weather = Weather(
                            airport_id=airport.id,
                            date=date.today(),
                            hour=datetime.now().hour,
                            temperature_celsius=weather_data.temperature_celsius,
                            humidity_percent=weather_data.humidity_percent,
                            wind_speed_mph=weather_data.wind_speed_mph,
                            wind_direction_degrees=weather_data.wind_direction_degrees,
                            visibility_miles=weather_data.visibility_miles,
                            precipitation_inches=weather_data.precipitation_inches,
                            conditions=weather_data.conditions,
                            delay_factor=weather_data.delay_factor,
                            cancellation_risk=weather_data.cancellation_risk
                        )
                        
                        # Check if weather data already exists for this hour
                        existing = Weather.query.filter_by(
                            airport_id=airport.id,
                            date=date.today(),
                            hour=datetime.now().hour
                        ).first()
                        
                        if existing:
                            # Update existing record
                            existing.temperature_celsius = weather_data.temperature_celsius
                            existing.humidity_percent = weather_data.humidity_percent
                            existing.wind_speed_mph = weather_data.wind_speed_mph
                            existing.wind_direction_degrees = weather_data.wind_direction_degrees
                            existing.visibility_miles = weather_data.visibility_miles
                            existing.precipitation_inches = weather_data.precipitation_inches
                            existing.conditions = weather_data.conditions
                            existing.delay_factor = weather_data.delay_factor
                            existing.cancellation_risk = weather_data.cancellation_risk
                        else:
                            # Add new record
                            db.session.add(weather)
                        
                        weather_count += 1
                        
                    # Rate limiting
                    time.sleep(0.1)
                    
                except Exception as e:
                    print(f"❌ Error updating weather for {airport.iata_code}: {e}")
            
            print(f"✅ Updated weather data for {weather_count} airports")
            
            print("✈️  Fetching real flight data...")
            flight_count = 0
            
            # Focus on major airports for flight data
            major_airports = [ap for ap in airports if ap.iata_code in [
                'ATL', 'LAX', 'ORD', 'DFW', 'DEN', 'JFK', 'SFO', 'SEA', 'LAS', 'MIA', 'BOS', 'PHX',
                'LHR', 'CDG', 'FRA', 'AMS', 'NRT', 'ICN', 'PEK', 'PVG', 'HKG', 'SIN', 'DXB'
            ]]
            
            for airport in major_airports:
                try:
                    flights = self.get_real_flights_for_airport(airport.iata_code)
                    
                    for flight_data in flights:
                        # Find or create airline
                        airline = Airline.query.filter_by(name=flight_data.airline).first()
                        if not airline:
                            airline_code = flight_data.flight_number[:2] if len(flight_data.flight_number) >= 2 else 'XX'
                            airline = Airline(
                                name=flight_data.airline,
                                iata_code=airline_code,
                                icao_code=airline_code,
                                country='US'
                            )
                            db.session.add(airline)
                            db.session.flush()
                        
                        # Find destination airport
                        dest_airport = Airport.query.filter_by(iata_code=flight_data.destination).first()
                        if not dest_airport:
                            continue  # Skip if destination not in our database
                        
                        # Find or create aircraft
                        aircraft = Aircraft.query.filter_by(type_code=flight_data.aircraft_type).first()
                        if not aircraft:
                            aircraft = Aircraft(
                                type_code=flight_data.aircraft_type,
                                manufacturer='Unknown',
                                model='Unknown',
                                capacity=150
                            )
                            db.session.add(aircraft)
                            db.session.flush()
                        
                        # Calculate delay percentage
                        duration_minutes = 180  # Default duration
                        delay_percentage = 0
                        if flight_data.delay_minutes > 0 and duration_minutes > 0:
                            delay_percentage = (flight_data.delay_minutes / duration_minutes) * 100
                        
                        # Create or update flight
                        existing_flight = Flight.query.filter_by(
                            flight_number=flight_data.flight_number,
                            flight_date=date.today()
                        ).first()
                        
                        if existing_flight:
                            # Update existing flight
                            existing_flight.actual_departure = flight_data.actual_departure
                            existing_flight.actual_arrival = flight_data.actual_arrival
                            existing_flight.status = flight_data.status
                            existing_flight.delay_minutes = flight_data.delay_minutes
                            existing_flight.delay_percentage = delay_percentage
                            existing_flight.gate = flight_data.gate
                            existing_flight.terminal = flight_data.terminal
                        else:
                            # Create new flight
                            flight = Flight(
                                flight_number=flight_data.flight_number,
                                airline_id=airline.id,
                                aircraft_id=aircraft.id,
                                origin_airport_id=airport.id,
                                destination_airport_id=dest_airport.id,
                                scheduled_departure=flight_data.scheduled_departure,
                                actual_departure=flight_data.actual_departure,
                                scheduled_arrival=flight_data.scheduled_arrival,
                                actual_arrival=flight_data.actual_arrival,
                                gate=flight_data.gate,
                                terminal=flight_data.terminal,
                                status=flight_data.status,
                                delay_minutes=flight_data.delay_minutes,
                                delay_percentage=delay_percentage,
                                seats_available=flight_data.seats_available,
                                total_seats=flight_data.total_seats,
                                load_factor=0.8,  # Default load factor
                                on_time_probability=0.8,  # Default probability
                                delay_probability=0.15,
                                cancellation_probability=0.02,
                                base_price=300.0,
                                current_price=300.0,
                                flight_date=date.today(),
                                duration_minutes=duration_minutes,
                                distance_miles=500,  # Default distance
                                route_frequency='DAILY'
                            )
                            db.session.add(flight)
                        
                        flight_count += 1
                    
                    # Rate limiting
                    time.sleep(1)
                    
                except Exception as e:
                    print(f"❌ Error updating flights for {airport.iata_code}: {e}")
            
            db.session.commit()
            print(f"✅ Updated flight data: {flight_count} flights")
            
            print(f"🎉 Real data integration complete!")
            print(f"📊 Updated {weather_count} weather records and {flight_count} flight records")

def main():
    """Main function to run real data integration"""
    print("🚀 Real Data Integration for Flight Delay Predictor")
    print("=" * 60)
    
    integrator = RealDataIntegrator()
    
    try:
        integrator.update_database_with_real_data()
        print(f"\n✅ Real data integration complete!")
        print(f"🌐 Visit http://localhost:8000 to see the real-time data")
        
    except Exception as e:
        print(f"\n❌ Error in real data integration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
