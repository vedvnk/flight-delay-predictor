#!/usr/bin/env python3
"""
Enhanced Flight Generator with Comprehensive Metrics
==================================================

This script generates comprehensive flight data with enhanced delay prediction metrics
including weather data, air traffic patterns, and historical performance data.
"""

import sys
import os
from datetime import datetime, timedelta, date
import random
import requests
import json
from typing import Dict, List, Optional

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from app import app
from models import db, Flight, Airport, Airline, Aircraft, Weather

class EnhancedFlightGenerator:
    """Generate enhanced flight data with comprehensive delay metrics"""
    
    def __init__(self):
        self.weather_api_key = None  # Will be set if available
        self.air_traffic_data = {}
        self.historical_performance = {}
        
    def add_comprehensive_airports(self):
        """Add comprehensive list of major airports worldwide"""
        print("🌍 Adding comprehensive airport data...")
        
        airports_data = [
            # Major US Airports
            {'iata': 'ATL', 'icao': 'KATL', 'name': 'Hartsfield-Jackson Atlanta International Airport', 'city': 'Atlanta', 'state': 'Georgia', 'country': 'United States', 'lat': 33.6407, 'lon': -84.4277, 'tz': 'America/New_York'},
            {'iata': 'LAX', 'icao': 'KLAX', 'name': 'Los Angeles International Airport', 'city': 'Los Angeles', 'state': 'California', 'country': 'United States', 'lat': 33.9425, 'lon': -118.4081, 'tz': 'America/Los_Angeles'},
            {'iata': 'ORD', 'icao': 'KORD', 'name': 'Chicago O\'Hare International Airport', 'city': 'Chicago', 'state': 'Illinois', 'country': 'United States', 'lat': 41.9786, 'lon': -87.9048, 'tz': 'America/Chicago'},
            {'iata': 'DFW', 'icao': 'KDFW', 'name': 'Dallas/Fort Worth International Airport', 'city': 'Dallas', 'state': 'Texas', 'country': 'United States', 'lat': 32.8968, 'lon': -97.0380, 'tz': 'America/Chicago'},
            {'iata': 'DEN', 'icao': 'KDEN', 'name': 'Denver International Airport', 'city': 'Denver', 'state': 'Colorado', 'country': 'United States', 'lat': 39.8561, 'lon': -104.6737, 'tz': 'America/Denver'},
            {'iata': 'JFK', 'icao': 'KJFK', 'name': 'John F. Kennedy International Airport', 'city': 'New York', 'state': 'New York', 'country': 'United States', 'lat': 40.6413, 'lon': -73.7781, 'tz': 'America/New_York'},
            {'iata': 'SFO', 'icao': 'KSFO', 'name': 'San Francisco International Airport', 'city': 'San Francisco', 'state': 'California', 'country': 'United States', 'lat': 37.6213, 'lon': -122.3790, 'tz': 'America/Los_Angeles'},
            {'iata': 'SEA', 'icao': 'KSEA', 'name': 'Seattle-Tacoma International Airport', 'city': 'Seattle', 'state': 'Washington', 'country': 'United States', 'lat': 47.4502, 'lon': -122.3088, 'tz': 'America/Los_Angeles'},
            {'iata': 'LAS', 'icao': 'KLAS', 'name': 'Harry Reid International Airport', 'city': 'Las Vegas', 'state': 'Nevada', 'country': 'United States', 'lat': 36.0840, 'lon': -115.1537, 'tz': 'America/Los_Angeles'},
            {'iata': 'MIA', 'icao': 'KMIA', 'name': 'Miami International Airport', 'city': 'Miami', 'state': 'Florida', 'country': 'United States', 'lat': 25.7959, 'lon': -80.2870, 'tz': 'America/New_York'},
            {'iata': 'BOS', 'icao': 'KBOS', 'name': 'Logan International Airport', 'city': 'Boston', 'state': 'Massachusetts', 'country': 'United States', 'lat': 42.3656, 'lon': -71.0096, 'tz': 'America/New_York'},
            {'iata': 'PHX', 'icao': 'KPHX', 'name': 'Phoenix Sky Harbor International Airport', 'city': 'Phoenix', 'state': 'Arizona', 'country': 'United States', 'lat': 33.4342, 'lon': -112.0116, 'tz': 'America/Phoenix'},
            {'iata': 'EWR', 'icao': 'KEWR', 'name': 'Newark Liberty International Airport', 'city': 'Newark', 'state': 'New Jersey', 'country': 'United States', 'lat': 40.6895, 'lon': -74.1745, 'tz': 'America/New_York'},
            {'iata': 'MCO', 'icao': 'KMCO', 'name': 'Orlando International Airport', 'city': 'Orlando', 'state': 'Florida', 'country': 'United States', 'lat': 28.4312, 'lon': -81.3081, 'tz': 'America/New_York'},
            {'iata': 'CLT', 'icao': 'KCLT', 'name': 'Charlotte Douglas International Airport', 'city': 'Charlotte', 'state': 'North Carolina', 'country': 'United States', 'lat': 35.2144, 'lon': -80.9473, 'tz': 'America/New_York'},
            {'iata': 'DTW', 'icao': 'KDTW', 'name': 'Detroit Metropolitan Wayne County Airport', 'city': 'Detroit', 'state': 'Michigan', 'country': 'United States', 'lat': 42.2162, 'lon': -83.3554, 'tz': 'America/New_York'},
            {'iata': 'PHL', 'icao': 'KPHL', 'name': 'Philadelphia International Airport', 'city': 'Philadelphia', 'state': 'Pennsylvania', 'country': 'United States', 'lat': 39.8729, 'lon': -75.2437, 'tz': 'America/New_York'},
            {'iata': 'LGA', 'icao': 'KLGA', 'name': 'LaGuardia Airport', 'city': 'New York', 'state': 'New York', 'country': 'United States', 'lat': 40.7769, 'lon': -73.8740, 'tz': 'America/New_York'},
            {'iata': 'BWI', 'icao': 'KBWI', 'name': 'Baltimore/Washington International Thurgood Marshall Airport', 'city': 'Baltimore', 'state': 'Maryland', 'country': 'United States', 'lat': 39.1774, 'lon': -76.6684, 'tz': 'America/New_York'},
            {'iata': 'IAD', 'icao': 'KIAD', 'name': 'Washington Dulles International Airport', 'city': 'Washington', 'state': 'Virginia', 'country': 'United States', 'lat': 38.9531, 'lon': -77.4565, 'tz': 'America/New_York'},
            {'iata': 'SLC', 'icao': 'KSLC', 'name': 'Salt Lake City International Airport', 'city': 'Salt Lake City', 'state': 'Utah', 'country': 'United States', 'lat': 40.7899, 'lon': -111.9791, 'tz': 'America/Denver'},
            {'iata': 'SAN', 'icao': 'KSAN', 'name': 'San Diego International Airport', 'city': 'San Diego', 'state': 'California', 'country': 'United States', 'lat': 32.7338, 'lon': -117.1933, 'tz': 'America/Los_Angeles'},
            {'iata': 'HNL', 'icao': 'PHNL', 'name': 'Daniel K. Inouye International Airport', 'city': 'Honolulu', 'state': 'Hawaii', 'country': 'United States', 'lat': 21.3187, 'lon': -157.9225, 'tz': 'Pacific/Honolulu'},
            {'iata': 'AUS', 'icao': 'KAUS', 'name': 'Austin-Bergstrom International Airport', 'city': 'Austin', 'state': 'Texas', 'country': 'United States', 'lat': 30.1945, 'lon': -97.6699, 'tz': 'America/Chicago'},
            {'iata': 'PDX', 'icao': 'KPDX', 'name': 'Portland International Airport', 'city': 'Portland', 'state': 'Oregon', 'country': 'United States', 'lat': 45.5898, 'lon': -122.5951, 'tz': 'America/Los_Angeles'},
            
            # Major International Airports
            {'iata': 'LHR', 'icao': 'EGLL', 'name': 'London Heathrow Airport', 'city': 'London', 'state': None, 'country': 'United Kingdom', 'lat': 51.4700, 'lon': -0.4543, 'tz': 'Europe/London'},
            {'iata': 'CDG', 'icao': 'LFPG', 'name': 'Charles de Gaulle Airport', 'city': 'Paris', 'state': None, 'country': 'France', 'lat': 49.0097, 'lon': 2.5479, 'tz': 'Europe/Paris'},
            {'iata': 'FRA', 'icao': 'EDDF', 'name': 'Frankfurt Airport', 'city': 'Frankfurt', 'state': None, 'country': 'Germany', 'lat': 50.0379, 'lon': 8.5622, 'tz': 'Europe/Berlin'},
            {'iata': 'AMS', 'icao': 'EHAM', 'name': 'Amsterdam Airport Schiphol', 'city': 'Amsterdam', 'state': None, 'country': 'Netherlands', 'lat': 52.3105, 'lon': 4.7683, 'tz': 'Europe/Amsterdam'},
            {'iata': 'MAD', 'icao': 'LEMD', 'name': 'Madrid-Barajas Airport', 'city': 'Madrid', 'state': None, 'country': 'Spain', 'lat': 40.4983, 'lon': -3.5676, 'tz': 'Europe/Madrid'},
            {'iata': 'FCO', 'icao': 'LIRF', 'name': 'Leonardo da Vinci International Airport', 'city': 'Rome', 'state': None, 'country': 'Italy', 'lat': 41.8045, 'lon': 12.2509, 'tz': 'Europe/Rome'},
            {'iata': 'ZUR', 'icao': 'LSZH', 'name': 'Zurich Airport', 'city': 'Zurich', 'state': None, 'country': 'Switzerland', 'lat': 47.4647, 'lon': 8.5492, 'tz': 'Europe/Zurich'},
            {'iata': 'VIE', 'icao': 'LOWW', 'name': 'Vienna International Airport', 'city': 'Vienna', 'state': None, 'country': 'Austria', 'lat': 48.1103, 'lon': 16.5697, 'tz': 'Europe/Vienna'},
            {'iata': 'DUB', 'icao': 'EIDW', 'name': 'Dublin Airport', 'city': 'Dublin', 'state': None, 'country': 'Ireland', 'lat': 53.4264, 'lon': -6.2499, 'tz': 'Europe/Dublin'},
            
            # Major Asian Airports
            {'iata': 'NRT', 'icao': 'RJAA', 'name': 'Narita International Airport', 'city': 'Tokyo', 'state': None, 'country': 'Japan', 'lat': 35.7720, 'lon': 140.3928, 'tz': 'Asia/Tokyo'},
            {'iata': 'ICN', 'icao': 'RKSI', 'name': 'Incheon International Airport', 'city': 'Seoul', 'state': None, 'country': 'South Korea', 'lat': 37.4602, 'lon': 126.4407, 'tz': 'Asia/Seoul'},
            {'iata': 'PEK', 'icao': 'ZBAA', 'name': 'Beijing Capital International Airport', 'city': 'Beijing', 'state': None, 'country': 'China', 'lat': 40.0799, 'lon': 116.6031, 'tz': 'Asia/Shanghai'},
            {'iata': 'PVG', 'icao': 'ZSPD', 'name': 'Shanghai Pudong International Airport', 'city': 'Shanghai', 'state': None, 'country': 'China', 'lat': 31.1434, 'lon': 121.8052, 'tz': 'Asia/Shanghai'},
            {'iata': 'HKG', 'icao': 'VHHH', 'name': 'Hong Kong International Airport', 'city': 'Hong Kong', 'state': None, 'country': 'Hong Kong', 'lat': 22.3080, 'lon': 113.9185, 'tz': 'Asia/Hong_Kong'},
            {'iata': 'SIN', 'icao': 'WSSS', 'name': 'Singapore Changi Airport', 'city': 'Singapore', 'state': None, 'country': 'Singapore', 'lat': 1.3644, 'lon': 103.9915, 'tz': 'Asia/Singapore'},
            {'iata': 'BKK', 'icao': 'VTBS', 'name': 'Suvarnabhumi Airport', 'city': 'Bangkok', 'state': None, 'country': 'Thailand', 'lat': 13.6900, 'lon': 100.7501, 'tz': 'Asia/Bangkok'},
            {'iata': 'DEL', 'icao': 'VIDP', 'name': 'Indira Gandhi International Airport', 'city': 'New Delhi', 'state': None, 'country': 'India', 'lat': 28.5562, 'lon': 77.1000, 'tz': 'Asia/Kolkata'},
            {'iata': 'BOM', 'icao': 'VABB', 'name': 'Chhatrapati Shivaji Maharaj International Airport', 'city': 'Mumbai', 'state': None, 'country': 'India', 'lat': 19.0896, 'lon': 72.8656, 'tz': 'Asia/Kolkata'},
            
            # Major Middle East/Africa Airports
            {'iata': 'DXB', 'icao': 'OMDB', 'name': 'Dubai International Airport', 'city': 'Dubai', 'state': None, 'country': 'United Arab Emirates', 'lat': 25.2532, 'lon': 55.3657, 'tz': 'Asia/Dubai'},
            {'iata': 'DOH', 'icao': 'OTHH', 'name': 'Hamad International Airport', 'city': 'Doha', 'state': None, 'country': 'Qatar', 'lat': 25.2611, 'lon': 51.5651, 'tz': 'Asia/Qatar'},
            {'iata': 'JNB', 'icao': 'FAOR', 'name': 'O.R. Tambo International Airport', 'city': 'Johannesburg', 'state': None, 'country': 'South Africa', 'lat': -26.1392, 'lon': 28.2460, 'tz': 'Africa/Johannesburg'},
            
            # Major Canadian Airports
            {'iata': 'YYZ', 'icao': 'CYYZ', 'name': 'Toronto Pearson International Airport', 'city': 'Toronto', 'state': 'Ontario', 'country': 'Canada', 'lat': 43.6777, 'lon': -79.6248, 'tz': 'America/Toronto'},
            {'iata': 'YVR', 'icao': 'CYVR', 'name': 'Vancouver International Airport', 'city': 'Vancouver', 'state': 'British Columbia', 'country': 'Canada', 'lat': 49.1967, 'lon': -123.1815, 'tz': 'America/Vancouver'},
            {'iata': 'YUL', 'icao': 'CYUL', 'name': 'Montreal-Pierre Elliott Trudeau International Airport', 'city': 'Montreal', 'state': 'Quebec', 'country': 'Canada', 'lat': 45.4706, 'lon': -73.7408, 'tz': 'America/Montreal'},
            
            # Major Australian Airports
            {'iata': 'SYD', 'icao': 'YSSY', 'name': 'Sydney Kingsford Smith Airport', 'city': 'Sydney', 'state': 'New South Wales', 'country': 'Australia', 'lat': -33.9399, 'lon': 151.1753, 'tz': 'Australia/Sydney'},
            {'iata': 'MEL', 'icao': 'YMML', 'name': 'Melbourne Airport', 'city': 'Melbourne', 'state': 'Victoria', 'country': 'Australia', 'lat': -37.6733, 'lon': 144.8433, 'tz': 'Australia/Melbourne'},
        ]
        
        with app.app_context():
            created_count = 0
            for airport_data in airports_data:
                existing = Airport.query.filter_by(iata_code=airport_data['iata']).first()
                if not existing:
                    airport = Airport(
                        iata_code=airport_data['iata'],
                        icao_code=airport_data['icao'],
                        name=airport_data['name'],
                        city=airport_data['city'],
                        state=airport_data['state'],
                        country=airport_data['country'],
                        latitude=airport_data['lat'],
                        longitude=airport_data['lon'],
                        timezone=airport_data['tz']
                    )
                    db.session.add(airport)
                    created_count += 1
            
            db.session.commit()
            print(f"✅ Added {created_count} new airports")
    
    def get_weather_data(self, airport_code: str, date: date) -> Optional[Dict]:
        """Get weather data for an airport on a specific date"""
        # For now, generate realistic weather data
        # In production, this would call a real weather API
        
        # Simulate weather patterns based on airport location and season
        base_temp = random.uniform(15, 25)  # Base temperature in Celsius
        humidity = random.uniform(40, 80)  # Humidity percentage
        wind_speed = random.uniform(5, 25)  # Wind speed in mph
        visibility = random.uniform(5, 15)  # Visibility in miles
        
        # Weather conditions
        conditions = random.choices(
            ['CLEAR', 'CLOUDY', 'PARTLY_CLOUDY', 'RAIN', 'THUNDERSTORM', 'SNOW'],
            weights=[40, 25, 20, 10, 3, 2]
        )[0]
        
        # Calculate delay factor based on conditions
        delay_factor = 1.0
        if conditions in ['THUNDERSTORM', 'SNOW']:
            delay_factor = random.uniform(1.5, 2.0)
        elif conditions == 'RAIN':
            delay_factor = random.uniform(1.2, 1.5)
        elif wind_speed > 20:
            delay_factor = random.uniform(1.1, 1.3)
        
        return {
            'temperature_celsius': base_temp,
            'humidity_percent': humidity,
            'wind_speed_mph': wind_speed,
            'wind_direction_degrees': random.uniform(0, 360),
            'visibility_miles': visibility,
            'precipitation_inches': random.uniform(0, 0.5) if conditions in ['RAIN', 'THUNDERSTORM'] else 0,
            'conditions': conditions,
            'delay_factor': delay_factor,
            'cancellation_risk': 0.05 if conditions == 'THUNDERSTORM' else 0.01
        }
    
    def get_air_traffic_delay_risk(self, airport_code: str, hour: int) -> float:
        """Calculate air traffic delay risk based on airport and time"""
        # Peak hours have higher delay risk
        peak_hours = [6, 7, 8, 9, 17, 18, 19, 20]
        if hour in peak_hours:
            return random.uniform(0.3, 0.7)
        elif hour in [10, 11, 12, 13, 14, 15, 16]:
            return random.uniform(0.1, 0.3)
        else:
            return random.uniform(0.05, 0.2)
    
    def get_historical_performance(self, route: str, airline: str) -> Dict:
        """Get historical performance data for a route and airline"""
        # Simulate historical performance data
        base_on_time = random.uniform(0.7, 0.9)
        base_delay = random.uniform(0.1, 0.25)
        base_cancellation = random.uniform(0.01, 0.05)
        
        return {
            'route_on_time_percentage': base_on_time,
            'airline_on_time_percentage': base_on_time + random.uniform(-0.05, 0.05),
            'average_delay_minutes': random.uniform(10, 30),
            'delay_probability': base_delay,
            'cancellation_probability': base_cancellation
        }
    
    def calculate_delay_percentage(self, delay_minutes: int, duration_minutes: int) -> float:
        """Calculate delay percentage relative to flight duration"""
        if duration_minutes <= 0:
            return 0.0
        return (delay_minutes / duration_minutes) * 100
    
    def generate_comprehensive_flights(self, days_ahead: int = 7):
        """Generate comprehensive flight data with enhanced metrics"""
        print("🛫 Generating comprehensive flight data with enhanced metrics...")
        
        with app.app_context():
            # Clear existing flights
            Flight.query.delete()
            Weather.query.delete()
            db.session.commit()
            print("✅ Cleared existing flights and weather data")
            
            # Get all airports, airlines, and aircraft
            airports = Airport.query.all()
            airlines = Airline.query.all()
            aircraft_types = Aircraft.query.all()
            
            if not airports or not airlines or not aircraft_types:
                print("❌ Missing required data (airports, airlines, or aircraft)")
                return
            
            # Generate flights for the next N days
            base_date = date.today()
            total_flights = 0
            
            for day_offset in range(days_ahead):
                flight_date = base_date + timedelta(days=day_offset)
                print(f"📅 Generating flights for {flight_date}")
                
                # Generate weather data for all airports
                weather_data = {}
                for airport in airports:
                    weather_data[airport.iata_code] = self.get_weather_data(airport.iata_code, flight_date)
                    
                    # Store weather data in database
                    for hour in range(24):
                        weather = Weather(
                            airport_id=airport.id,
                            date=flight_date,
                            hour=hour,
                            **weather_data[airport.iata_code]
                        )
                        db.session.add(weather)
                
                # Generate flights for this date
                flights_this_day = 0
                
                # Create routes between major airports
                major_airports = [ap for ap in airports if ap.iata_code in [
                    'ATL', 'LAX', 'ORD', 'DFW', 'DEN', 'JFK', 'SFO', 'SEA', 'LAS', 'MIA', 'BOS', 'PHX',
                    'LHR', 'CDG', 'FRA', 'AMS', 'NRT', 'ICN', 'PEK', 'PVG', 'HKG', 'SIN', 'DXB'
                ]]
                
                for origin in major_airports:
                    for destination in major_airports:
                        if origin.id != destination.id:
                            # Generate 2-5 flights per route per day
                            num_flights = random.randint(2, 5)
                            
                            for flight_num in range(num_flights):
                                # Random departure time
                                departure_hour = random.randint(5, 23)
                                departure_minute = random.randint(0, 59)
                                scheduled_departure = datetime.combine(
                                    flight_date, 
                                    datetime.min.time().replace(hour=departure_hour, minute=departure_minute)
                                )
                                
                                # Calculate flight duration (simplified)
                                distance = random.randint(200, 3000)  # miles
                                duration_minutes = distance // 5 + random.randint(30, 60)
                                
                                scheduled_arrival = scheduled_departure + timedelta(minutes=duration_minutes)
                                
                                # Select random airline and aircraft
                                airline = random.choice(airlines)
                                aircraft = random.choice(aircraft_types)
                                
                                # Get historical performance
                                route_key = f"{origin.iata_code}-{destination.iata_code}"
                                hist_perf = self.get_historical_performance(route_key, airline.name)
                                
                                # Calculate delay metrics
                                weather_delay = random.randint(0, 30) if weather_data[origin.iata_code]['delay_factor'] > 1.2 else random.randint(0, 10)
                                air_traffic_delay = random.randint(0, 20) if self.get_air_traffic_delay_risk(origin.iata_code, departure_hour) > 0.3 else random.randint(0, 5)
                                security_delay = random.randint(0, 15)
                                mechanical_delay = random.randint(0, 10) if random.random() < 0.1 else 0
                                crew_delay = random.randint(0, 20) if random.random() < 0.05 else 0
                                
                                total_delay = weather_delay + air_traffic_delay + security_delay + mechanical_delay + crew_delay
                                
                                # Determine status
                                if total_delay > 60:
                                    status = 'CANCELLED'
                                elif total_delay > 15:
                                    status = 'DELAYED'
                                else:
                                    status = 'ON_TIME'
                                
                                # Calculate delay percentage
                                delay_percentage = self.calculate_delay_percentage(total_delay, duration_minutes)
                                
                                # Calculate time-based delay factors
                                time_of_day_factor = 1.0
                                if departure_hour in [6, 7, 8, 9, 17, 18, 19, 20]:
                                    time_of_day_factor = random.uniform(1.2, 1.5)
                                elif departure_hour in [22, 23, 0, 1, 2, 3, 4, 5]:
                                    time_of_day_factor = random.uniform(0.8, 1.0)
                                
                                day_of_week_factor = 1.0
                                if flight_date.weekday() in [4, 5, 6]:  # Weekend
                                    day_of_week_factor = random.uniform(1.1, 1.3)
                                
                                seasonal_factor = 1.0
                                if flight_date.month in [12, 1, 2]:  # Winter
                                    seasonal_factor = random.uniform(1.1, 1.4)
                                elif flight_date.month in [6, 7, 8]:  # Summer
                                    seasonal_factor = random.uniform(1.0, 1.2)
                                
                                # Create flight
                                flight = Flight(
                                    flight_number=f"{airline.iata_code}{random.randint(100, 9999)}",
                                    airline_id=airline.id,
                                    aircraft_id=aircraft.id,
                                    origin_airport_id=origin.id,
                                    destination_airport_id=destination.id,
                                    scheduled_departure=scheduled_departure,
                                    actual_departure=scheduled_departure + timedelta(minutes=total_delay) if status != 'CANCELLED' else None,
                                    scheduled_arrival=scheduled_arrival,
                                    actual_arrival=scheduled_arrival + timedelta(minutes=total_delay) if status != 'CANCELLED' else None,
                                    gate=f"{random.choice(['A', 'B', 'C', 'D', 'E'])}{random.randint(1, 50)}",
                                    terminal=f"T{random.randint(1, 5)}",
                                    status=status,
                                    delay_minutes=total_delay if status != 'CANCELLED' else 0,
                                    delay_percentage=delay_percentage,
                                    seats_available=random.randint(0, 200),
                                    total_seats=random.randint(150, 400),
                                    load_factor=random.uniform(0.6, 0.95),
                                    on_time_probability=hist_perf['route_on_time_percentage'],
                                    delay_probability=hist_perf['delay_probability'],
                                    cancellation_probability=hist_perf['cancellation_probability'],
                                    base_price=random.uniform(200, 1200),
                                    current_price=random.uniform(200, 1200),
                                    flight_date=flight_date,
                                    duration_minutes=duration_minutes,
                                    distance_miles=distance,
                                    route_frequency='DAILY',
                                    
                                    # NEW: Comprehensive delay metrics
                                    air_traffic_delay_minutes=air_traffic_delay,
                                    weather_delay_minutes=weather_delay,
                                    security_delay_minutes=security_delay,
                                    mechanical_delay_minutes=mechanical_delay,
                                    crew_delay_minutes=crew_delay,
                                    
                                    # Historical performance metrics
                                    route_on_time_percentage=hist_perf['route_on_time_percentage'],
                                    airline_on_time_percentage=hist_perf['airline_on_time_percentage'],
                                    time_of_day_delay_factor=time_of_day_factor,
                                    day_of_week_delay_factor=day_of_week_factor,
                                    seasonal_delay_factor=seasonal_factor,
                                    
                                    # Real-time conditions
                                    current_weather_delay_risk=weather_data[origin.iata_code]['delay_factor'] - 1.0,
                                    current_air_traffic_delay_risk=self.get_air_traffic_delay_risk(origin.iata_code, departure_hour),
                                    current_airport_congestion_level=random.uniform(0.3, 0.8)
                                )
                                
                                db.session.add(flight)
                                flights_this_day += 1
                                total_flights += 1
                
                db.session.commit()
                print(f"✅ Generated {flights_this_day} flights for {flight_date}")
            
            print(f"🎉 Generated {total_flights} comprehensive flights with enhanced metrics!")
            
            # Show sample data
            sample_flights = Flight.query.options(
                db.joinedload(Flight.airline),
                db.joinedload(Flight.origin_airport),
                db.joinedload(Flight.destination_airport)
            ).limit(5).all()
            
            print(f"\n📋 Sample enhanced flights:")
            for flight in sample_flights:
                origin = flight.origin_airport.iata_code if flight.origin_airport else 'Unknown'
                dest = flight.destination_airport.iata_code if flight.destination_airport else 'Unknown'
                airline = flight.airline.name if flight.airline else 'Unknown'
                print(f"   {flight.flight_number} - {airline} {origin}→{dest} - {flight.status}")
                print(f"      Delay: {flight.delay_minutes}min ({flight.delay_percentage:.1f}%)")
                print(f"      Weather Risk: {flight.current_weather_delay_risk:.2f}")
                print(f"      Air Traffic Risk: {flight.current_air_traffic_delay_risk:.2f}")

def main():
    """Main function to generate enhanced flight data"""
    print("🚀 Enhanced Flight Generator with Comprehensive Metrics")
    print("=" * 60)
    
    generator = EnhancedFlightGenerator()
    
    try:
        # Add comprehensive airports
        generator.add_comprehensive_airports()
        
        # Generate comprehensive flights
        generator.generate_comprehensive_flights(days_ahead=7)
        
        print(f"\n✅ Enhanced flight data generation complete!")
        print(f"🌐 Visit http://localhost:8000 to see the enhanced data")
        
    except Exception as e:
        print(f"\n❌ Error generating enhanced flight data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
