#!/usr/bin/env python3
"""
Generate More Real Flights
=========================

This script generates additional realistic flight data across multiple routes,
airlines, and airports to expand the database with more comprehensive coverage.
"""

import sys
import os
from datetime import datetime, timedelta, date
import random
from typing import Dict, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from app import app
from models import db, Flight, Airport, Airline, Aircraft
from delay_reason_analyzer import DelayReasonAnalyzer, DelayReason

class MoreRealFlightsGenerator:
    """Generate more realistic flight data"""
    
    def __init__(self):
        self.delay_analyzer = DelayReasonAnalyzer()
        
        # Comprehensive airline data with realistic on-time rates
        self.airlines_data = [
            {'name': 'American Airlines', 'code': 'AA', 'on_time_rate': 0.78, 'country': 'US'},
            {'name': 'United Airlines', 'code': 'UA', 'on_time_rate': 0.82, 'country': 'US'},
            {'name': 'Delta Air Lines', 'code': 'DL', 'on_time_rate': 0.85, 'country': 'US'},
            {'name': 'Southwest Airlines', 'code': 'WN', 'on_time_rate': 0.79, 'country': 'US'},
            {'name': 'JetBlue Airways', 'code': 'B6', 'on_time_rate': 0.83, 'country': 'US'},
            {'name': 'Alaska Airlines', 'code': 'AS', 'on_time_rate': 0.87, 'country': 'US'},
            {'name': 'Spirit Airlines', 'code': 'NK', 'on_time_rate': 0.75, 'country': 'US'},
            {'name': 'Frontier Airlines', 'code': 'F9', 'on_time_rate': 0.74, 'country': 'US'},
            {'name': 'Hawaiian Airlines', 'code': 'HA', 'on_time_rate': 0.89, 'country': 'US'},
            {'name': 'Allegiant Air', 'code': 'G4', 'on_time_rate': 0.73, 'country': 'US'},
            {'name': 'British Airways', 'code': 'BA', 'on_time_rate': 0.81, 'country': 'UK'},
            {'name': 'Lufthansa', 'code': 'LH', 'on_time_rate': 0.84, 'country': 'Germany'},
            {'name': 'Air France', 'code': 'AF', 'on_time_rate': 0.80, 'country': 'France'},
            {'name': 'KLM Royal Dutch Airlines', 'code': 'KL', 'on_time_rate': 0.83, 'country': 'Netherlands'},
            {'name': 'Air Canada', 'code': 'AC', 'on_time_rate': 0.86, 'country': 'Canada'},
            {'name': 'Emirates', 'code': 'EK', 'on_time_rate': 0.88, 'country': 'UAE'},
            {'name': 'Qatar Airways', 'code': 'QR', 'on_time_rate': 0.87, 'country': 'Qatar'},
            {'name': 'Singapore Airlines', 'code': 'SQ', 'on_time_rate': 0.90, 'country': 'Singapore'},
            {'name': 'Japan Airlines', 'code': 'JL', 'on_time_rate': 0.89, 'country': 'Japan'},
            {'name': 'All Nippon Airways', 'code': 'NH', 'on_time_rate': 0.91, 'country': 'Japan'},
            {'name': 'Korean Air', 'code': 'KE', 'on_time_rate': 0.88, 'country': 'South Korea'},
            {'name': 'Cathay Pacific', 'code': 'CX', 'on_time_rate': 0.86, 'country': 'Hong Kong'},
            {'name': 'Turkish Airlines', 'code': 'TK', 'on_time_rate': 0.82, 'country': 'Turkey'},
            {'name': 'Swiss International Air Lines', 'code': 'LX', 'on_time_rate': 0.85, 'country': 'Switzerland'},
            {'name': 'Austrian Airlines', 'code': 'OS', 'on_time_rate': 0.83, 'country': 'Austria'},
            {'name': 'SAS Scandinavian Airlines', 'code': 'SK', 'on_time_rate': 0.81, 'country': 'Sweden'},
            {'name': 'Finnair', 'code': 'AY', 'on_time_rate': 0.84, 'country': 'Finland'},
            {'name': 'Iberia', 'code': 'IB', 'on_time_rate': 0.79, 'country': 'Spain'},
            {'name': 'Alitalia', 'code': 'AZ', 'on_time_rate': 0.77, 'country': 'Italy'},
            {'name': 'Virgin Atlantic', 'code': 'VS', 'on_time_rate': 0.82, 'country': 'UK'},
        ]
        
        # Comprehensive route data
        self.routes_data = [
            # Major US domestic routes
            {'from': 'LAX', 'to': 'ORD', 'frequency': 'high', 'distance': 1745, 'typical_duration': 240},
            {'from': 'LAX', 'to': 'JFK', 'frequency': 'high', 'distance': 2475, 'typical_duration': 330},
            {'from': 'LAX', 'to': 'DFW', 'frequency': 'high', 'distance': 1235, 'typical_duration': 180},
            {'from': 'LAX', 'to': 'DEN', 'frequency': 'high', 'distance': 862, 'typical_duration': 150},
            {'from': 'LAX', 'to': 'SFO', 'frequency': 'very_high', 'distance': 337, 'typical_duration': 90},
            {'from': 'LAX', 'to': 'SEA', 'frequency': 'high', 'distance': 954, 'typical_duration': 165},
            {'from': 'LAX', 'to': 'LAS', 'frequency': 'high', 'distance': 236, 'typical_duration': 75},
            {'from': 'LAX', 'to': 'PHX', 'frequency': 'high', 'distance': 370, 'typical_duration': 90},
            {'from': 'LAX', 'to': 'ATL', 'frequency': 'medium', 'distance': 1947, 'typical_duration': 270},
            {'from': 'LAX', 'to': 'MIA', 'frequency': 'medium', 'distance': 2338, 'typical_duration': 300},
            {'from': 'LAX', 'to': 'BOS', 'frequency': 'medium', 'distance': 2611, 'typical_duration': 330},
            {'from': 'LAX', 'to': 'IAH', 'frequency': 'high', 'distance': 1387, 'typical_duration': 195},
            {'from': 'LAX', 'to': 'MSP', 'frequency': 'medium', 'distance': 1535, 'typical_duration': 210},
            {'from': 'LAX', 'to': 'DTW', 'frequency': 'medium', 'distance': 1950, 'typical_duration': 270},
            {'from': 'LAX', 'to': 'CLT', 'frequency': 'medium', 'distance': 2143, 'typical_duration': 285},
            
            # ORD routes
            {'from': 'ORD', 'to': 'JFK', 'frequency': 'very_high', 'distance': 740, 'typical_duration': 120},
            {'from': 'ORD', 'to': 'LGA', 'frequency': 'very_high', 'distance': 733, 'typical_duration': 120},
            {'from': 'ORD', 'to': 'DFW', 'frequency': 'high', 'distance': 925, 'typical_duration': 135},
            {'from': 'ORD', 'to': 'DEN', 'frequency': 'high', 'distance': 888, 'typical_duration': 135},
            {'from': 'ORD', 'to': 'SFO', 'frequency': 'high', 'distance': 1850, 'typical_duration': 270},
            {'from': 'ORD', 'to': 'SEA', 'frequency': 'high', 'distance': 1721, 'typical_duration': 255},
            {'from': 'ORD', 'to': 'LAS', 'frequency': 'high', 'distance': 1519, 'typical_duration': 225},
            {'from': 'ORD', 'to': 'ATL', 'frequency': 'very_high', 'distance': 606, 'typical_duration': 105},
            {'from': 'ORD', 'to': 'MIA', 'frequency': 'high', 'distance': 1198, 'typical_duration': 180},
            {'from': 'ORD', 'to': 'BOS', 'frequency': 'high', 'distance': 867, 'typical_duration': 135},
            {'from': 'ORD', 'to': 'IAH', 'frequency': 'high', 'distance': 925, 'typical_duration': 135},
            {'from': 'ORD', 'to': 'MSP', 'frequency': 'high', 'distance': 334, 'typical_duration': 75},
            {'from': 'ORD', 'to': 'DTW', 'frequency': 'high', 'distance': 235, 'typical_duration': 60},
            {'from': 'ORD', 'to': 'CLT', 'frequency': 'high', 'distance': 586, 'typical_duration': 105},
            
            # JFK routes
            {'from': 'JFK', 'to': 'LGA', 'frequency': 'very_high', 'distance': 14, 'typical_duration': 30},
            {'from': 'JFK', 'to': 'EWR', 'frequency': 'very_high', 'distance': 18, 'typical_duration': 30},
            {'from': 'JFK', 'to': 'DFW', 'frequency': 'high', 'distance': 1394, 'typical_duration': 210},
            {'from': 'JFK', 'to': 'DEN', 'frequency': 'high', 'distance': 1626, 'typical_duration': 240},
            {'from': 'JFK', 'to': 'SFO', 'frequency': 'high', 'distance': 2585, 'typical_duration': 360},
            {'from': 'JFK', 'to': 'SEA', 'frequency': 'high', 'distance': 2420, 'typical_duration': 330},
            {'from': 'JFK', 'to': 'ATL', 'frequency': 'very_high', 'distance': 760, 'typical_duration': 120},
            {'from': 'JFK', 'to': 'MIA', 'frequency': 'high', 'distance': 1094, 'typical_duration': 165},
            {'from': 'JFK', 'to': 'BOS', 'frequency': 'very_high', 'distance': 190, 'typical_duration': 60},
            {'from': 'JFK', 'to': 'IAH', 'frequency': 'high', 'distance': 1419, 'typical_duration': 210},
            
            # International routes
            {'from': 'JFK', 'to': 'LHR', 'frequency': 'high', 'distance': 3451, 'typical_duration': 480},
            {'from': 'JFK', 'to': 'CDG', 'frequency': 'high', 'distance': 3635, 'typical_duration': 480},
            {'from': 'JFK', 'to': 'FRA', 'frequency': 'high', 'distance': 3851, 'typical_duration': 480},
            {'from': 'JFK', 'to': 'AMS', 'frequency': 'medium', 'distance': 3635, 'typical_duration': 480},
            {'from': 'JFK', 'to': 'NRT', 'frequency': 'medium', 'distance': 6745, 'typical_duration': 840},
            {'from': 'JFK', 'to': 'ICN', 'frequency': 'medium', 'distance': 6800, 'typical_duration': 840},
            {'from': 'JFK', 'to': 'PEK', 'frequency': 'medium', 'distance': 6840, 'typical_duration': 840},
            {'from': 'JFK', 'to': 'PVG', 'frequency': 'medium', 'distance': 7340, 'typical_duration': 900},
            {'from': 'JFK', 'to': 'HKG', 'frequency': 'medium', 'distance': 8070, 'typical_duration': 960},
            {'from': 'JFK', 'to': 'DXB', 'frequency': 'medium', 'distance': 6830, 'typical_duration': 840},
            
            # LAX international routes
            {'from': 'LAX', 'to': 'NRT', 'frequency': 'high', 'distance': 5470, 'typical_duration': 660},
            {'from': 'LAX', 'to': 'ICN', 'frequency': 'medium', 'distance': 5930, 'typical_duration': 720},
            {'from': 'LAX', 'to': 'PEK', 'frequency': 'medium', 'distance': 6260, 'typical_duration': 750},
            {'from': 'LAX', 'to': 'PVG', 'frequency': 'medium', 'distance': 6240, 'typical_duration': 750},
            {'from': 'LAX', 'to': 'HKG', 'frequency': 'medium', 'distance': 7260, 'typical_duration': 870},
            {'from': 'LAX', 'to': 'SIN', 'frequency': 'low', 'distance': 8750, 'typical_duration': 1050},
            {'from': 'LAX', 'to': 'SYD', 'frequency': 'medium', 'distance': 7485, 'typical_duration': 900},
            {'from': 'LAX', 'to': 'LHR', 'frequency': 'medium', 'distance': 5450, 'typical_duration': 660},
            {'from': 'LAX', 'to': 'CDG', 'frequency': 'medium', 'distance': 5660, 'typical_duration': 660},
            {'from': 'LAX', 'to': 'FRA', 'frequency': 'medium', 'distance': 5750, 'typical_duration': 660},
            
            # SFO routes
            {'from': 'SFO', 'to': 'SEA', 'frequency': 'high', 'distance': 679, 'typical_duration': 120},
            {'from': 'SFO', 'to': 'LAS', 'frequency': 'high', 'distance': 414, 'typical_duration': 90},
            {'from': 'SFO', 'to': 'PHX', 'frequency': 'high', 'distance': 651, 'typical_duration': 120},
            {'from': 'SFO', 'to': 'DEN', 'frequency': 'high', 'distance': 967, 'typical_duration': 150},
            {'from': 'SFO', 'to': 'DFW', 'frequency': 'high', 'distance': 1464, 'typical_duration': 210},
            {'from': 'SFO', 'to': 'ORD', 'frequency': 'high', 'distance': 1850, 'typical_duration': 270},
            {'from': 'SFO', 'to': 'JFK', 'frequency': 'high', 'distance': 2585, 'typical_duration': 360},
            {'from': 'SFO', 'to': 'ATL', 'frequency': 'medium', 'distance': 2134, 'typical_duration': 300},
            {'from': 'SFO', 'to': 'MIA', 'frequency': 'medium', 'distance': 2585, 'typical_duration': 360},
            {'from': 'SFO', 'to': 'BOS', 'frequency': 'medium', 'distance': 2700, 'typical_duration': 360},
            
            # SEA routes
            {'from': 'SEA', 'to': 'LAS', 'frequency': 'high', 'distance': 867, 'typical_duration': 135},
            {'from': 'SEA', 'to': 'PHX', 'frequency': 'high', 'distance': 1107, 'typical_duration': 165},
            {'from': 'SEA', 'to': 'DEN', 'frequency': 'high', 'distance': 1024, 'typical_duration': 150},
            {'from': 'SEA', 'to': 'DFW', 'frequency': 'high', 'distance': 1664, 'typical_duration': 240},
            {'from': 'SEA', 'to': 'ORD', 'frequency': 'high', 'distance': 1721, 'typical_duration': 255},
            {'from': 'SEA', 'to': 'JFK', 'frequency': 'high', 'distance': 2420, 'typical_duration': 330},
            {'from': 'SEA', 'to': 'ATL', 'frequency': 'medium', 'distance': 2181, 'typical_duration': 300},
            {'from': 'SEA', 'to': 'MIA', 'frequency': 'medium', 'distance': 2730, 'typical_duration': 360},
            {'from': 'SEA', 'to': 'BOS', 'frequency': 'medium', 'distance': 2498, 'typical_duration': 330},
            {'from': 'SEA', 'to': 'IAH', 'frequency': 'high', 'distance': 1890, 'typical_duration': 270},
            
            # DFW routes
            {'from': 'DFW', 'to': 'DEN', 'frequency': 'high', 'distance': 641, 'typical_duration': 105},
            {'from': 'DFW', 'to': 'LAS', 'frequency': 'high', 'distance': 1024, 'typical_duration': 150},
            {'from': 'DFW', 'to': 'PHX', 'frequency': 'high', 'distance': 865, 'typical_duration': 120},
            {'from': 'DFW', 'to': 'ORD', 'frequency': 'high', 'distance': 925, 'typical_duration': 135},
            {'from': 'DFW', 'to': 'JFK', 'frequency': 'high', 'distance': 1394, 'typical_duration': 210},
            {'from': 'DFW', 'to': 'ATL', 'frequency': 'very_high', 'distance': 781, 'typical_duration': 120},
            {'from': 'DFW', 'to': 'MIA', 'frequency': 'high', 'distance': 1120, 'typical_duration': 165},
            {'from': 'DFW', 'to': 'BOS', 'frequency': 'high', 'distance': 1565, 'typical_duration': 225},
            {'from': 'DFW', 'to': 'IAH', 'frequency': 'very_high', 'distance': 225, 'typical_duration': 45},
            {'from': 'DFW', 'to': 'CLT', 'frequency': 'high', 'distance': 925, 'typical_duration': 135},
            
            # DEN routes
            {'from': 'DEN', 'to': 'LAS', 'frequency': 'high', 'distance': 628, 'typical_duration': 90},
            {'from': 'DEN', 'to': 'PHX', 'frequency': 'high', 'distance': 602, 'typical_duration': 90},
            {'from': 'DEN', 'to': 'ORD', 'frequency': 'high', 'distance': 888, 'typical_duration': 135},
            {'from': 'DEN', 'to': 'JFK', 'frequency': 'high', 'distance': 1626, 'typical_duration': 240},
            {'from': 'DEN', 'to': 'ATL', 'frequency': 'high', 'distance': 1198, 'typical_duration': 180},
            {'from': 'DEN', 'to': 'MIA', 'frequency': 'high', 'distance': 1544, 'typical_duration': 225},
            {'from': 'DEN', 'to': 'BOS', 'frequency': 'high', 'distance': 1750, 'typical_duration': 255},
            {'from': 'DEN', 'to': 'IAH', 'frequency': 'high', 'distance': 925, 'typical_duration': 135},
            {'from': 'DEN', 'to': 'CLT', 'frequency': 'high', 'distance': 1394, 'typical_duration': 210},
            {'from': 'DEN', 'to': 'MSP', 'frequency': 'high', 'distance': 680, 'typical_duration': 105},
        ]
        
        # Aircraft types with realistic data
        self.aircraft_types = [
            {'type': 'B737', 'manufacturer': 'Boeing', 'model': '737', 'capacity': 150, 'range': 3500},
            {'type': 'B777', 'manufacturer': 'Boeing', 'model': '777', 'capacity': 300, 'range': 9700},
            {'type': 'B787', 'manufacturer': 'Boeing', 'model': '787', 'capacity': 250, 'range': 8500},
            {'type': 'B747', 'manufacturer': 'Boeing', 'model': '747', 'capacity': 400, 'range': 8000},
            {'type': 'A320', 'manufacturer': 'Airbus', 'model': 'A320', 'capacity': 150, 'range': 3700},
            {'type': 'A321', 'manufacturer': 'Airbus', 'model': 'A321', 'capacity': 180, 'range': 4000},
            {'type': 'A330', 'manufacturer': 'Airbus', 'model': 'A330', 'capacity': 250, 'range': 7400},
            {'type': 'A350', 'manufacturer': 'Airbus', 'model': 'A350', 'capacity': 280, 'range': 9700},
            {'type': 'A380', 'manufacturer': 'Airbus', 'model': 'A380', 'capacity': 500, 'range': 8000},
            {'type': 'E190', 'manufacturer': 'Embraer', 'model': 'E190', 'capacity': 100, 'range': 2400},
            {'type': 'CRJ900', 'manufacturer': 'Bombardier', 'model': 'CRJ900', 'capacity': 90, 'range': 2200},
            {'type': 'ATR72', 'manufacturer': 'ATR', 'model': 'ATR72', 'capacity': 70, 'range': 1500},
        ]
    
    def generate_comprehensive_flights(self, days_ahead: int = 3):
        """Generate comprehensive flight data across multiple routes"""
        print("🛫 Generating comprehensive flight data...")
        
        with app.app_context():
            # Get all airports, airlines, and aircraft
            airports = {ap.iata_code: ap for ap in Airport.query.all()}
            airlines = {al.name: al for al in Airline.query.all()}
            aircraft = {ac.type_code: ac for ac in Aircraft.query.all()}
            
            total_flights_generated = 0
            
            # Generate flights for the next N days
            base_date = date.today()
            
            for day_offset in range(days_ahead):
                flight_date = base_date + timedelta(days=day_offset)
                print(f"📅 Generating flights for {flight_date}")
                
                flights_this_day = 0
                
                for route_data in self.routes_data:
                    origin_code = route_data['from']
                    destination_code = route_data['to']
                    
                    # Check if both airports exist
                    if origin_code not in airports or destination_code not in airports:
                        continue
                    
                    origin_airport = airports[origin_code]
                    destination_airport = airports[destination_code]
                    
                    # Determine number of flights based on frequency
                    frequency = route_data['frequency']
                    if frequency == 'very_high':
                        num_flights = random.randint(8, 15)
                    elif frequency == 'high':
                        num_flights = random.randint(5, 10)
                    elif frequency == 'medium':
                        num_flights = random.randint(3, 7)
                    else:  # low
                        num_flights = random.randint(1, 3)
                    
                    # Generate flights for this route
                    for flight_num in range(num_flights):
                        # Select random airline
                        airline_data = random.choice(self.airlines_data)
                        airline_name = airline_data['name']
                        
                        # Find or create airline
                        if airline_name in airlines:
                            airline = airlines[airline_name]
                        else:
                            airline = Airline(
                                name=airline_name,
                                iata_code=airline_data['code'],
                                icao_code=airline_data['code'],
                                country=airline_data['country']
                            )
                            db.session.add(airline)
                            db.session.flush()
                            airlines[airline_name] = airline
                        
                        # Select random aircraft
                        aircraft_data = random.choice(self.aircraft_types)
                        aircraft_type = aircraft_data['type']
                        
                        if aircraft_type in aircraft:
                            aircraft_obj = aircraft[aircraft_type]
                        else:
                            aircraft_obj = Aircraft(
                                type_code=aircraft_type,
                                manufacturer=aircraft_data['manufacturer'],
                                model=aircraft_data['model'],
                                capacity=aircraft_data['capacity']
                            )
                            db.session.add(aircraft_obj)
                            db.session.flush()
                            aircraft[aircraft_type] = aircraft_obj
                        
                        # Generate flight times
                        hour = random.randint(5, 23)
                        minute = random.choice([0, 15, 30, 45])
                        scheduled_departure = datetime.combine(
                            flight_date, 
                            datetime.min.time().replace(hour=hour, minute=minute)
                        )
                        
                        # Calculate flight duration
                        base_duration = route_data['typical_duration']
                        duration_variation = random.randint(-30, 30)
                        duration_minutes = max(60, base_duration + duration_variation)
                        
                        scheduled_arrival = scheduled_departure + timedelta(minutes=duration_minutes)
                        
                        # Generate realistic delays
                        delay_breakdown = self._calculate_realistic_delays(
                            airline_data['on_time_rate'], hour, route_data
                        )
                        
                        total_delay = sum(delay_breakdown.values())
                        
                        # Determine status
                        if total_delay > 60:
                            status = 'CANCELLED'
                        elif total_delay > 15:
                            status = 'DELAYED'
                        else:
                            status = 'ON_TIME'
                        
                        # Calculate delay percentage
                        delay_percentage = (total_delay / duration_minutes) * 100 if duration_minutes > 0 else 0
                        
                        # Generate flight number
                        flight_number = f"{airline_data['code']}{random.randint(100, 9999)}"
                        
                        # Create flight data for delay analysis
                        flight_data = {
                            'delay_minutes': total_delay,
                            'weather_delay_minutes': delay_breakdown['weather'],
                            'air_traffic_delay_minutes': delay_breakdown['air_traffic'],
                            'security_delay_minutes': delay_breakdown['security'],
                            'mechanical_delay_minutes': delay_breakdown['mechanical'],
                            'crew_delay_minutes': delay_breakdown['crew'],
                            'current_weather_delay_risk': random.uniform(0.1, 0.3),
                            'current_air_traffic_delay_risk': random.uniform(0.1, 0.4),
                            'scheduled_departure': scheduled_departure
                        }
                        
                        # Analyze delay reasons
                        analysis = self.delay_analyzer.analyze_delay_reasons(flight_data)
                        
                        # Calculate performance metrics
                        route_on_time_percentage = airline_data['on_time_rate'] + random.uniform(-0.05, 0.05)
                        airline_on_time_percentage = airline_data['on_time_rate'] + random.uniform(-0.03, 0.03)
                        
                        # Calculate time-based factors
                        time_of_day_factor = self._calculate_time_delay_factor(hour)
                        day_of_week_factor = self._calculate_day_delay_factor(flight_date.weekday())
                        seasonal_factor = self._calculate_seasonal_delay_factor(flight_date.month)
                        
                        # Create flight
                        flight = Flight(
                            flight_number=flight_number,
                            airline_id=airline.id,
                            aircraft_id=aircraft_obj.id,
                            origin_airport_id=origin_airport.id,
                            destination_airport_id=destination_airport.id,
                            scheduled_departure=scheduled_departure,
                            actual_departure=scheduled_departure + timedelta(minutes=total_delay) if status != 'CANCELLED' else None,
                            scheduled_arrival=scheduled_arrival,
                            actual_arrival=scheduled_arrival + timedelta(minutes=total_delay) if status != 'CANCELLED' else None,
                            gate=f"{random.choice(['A', 'B', 'C', 'D', 'E'])}{random.randint(1, 50)}",
                            terminal=f"T{random.randint(1, 5)}",
                            status=status,
                            delay_minutes=total_delay if status != 'CANCELLED' else 0,
                            delay_percentage=delay_percentage,
                            seats_available=random.randint(0, aircraft_data['capacity']),
                            total_seats=aircraft_data['capacity'],
                            load_factor=random.uniform(0.6, 0.95),
                            on_time_probability=route_on_time_percentage,
                            delay_probability=1 - route_on_time_percentage,
                            cancellation_probability=0.02,
                            base_price=random.uniform(200, 1200),
                            current_price=random.uniform(200, 1200),
                            flight_date=flight_date,
                            duration_minutes=duration_minutes,
                            distance_miles=route_data['distance'],
                            route_frequency='DAILY',
                            
                            # Comprehensive delay metrics
                            weather_delay_minutes=delay_breakdown['weather'],
                            air_traffic_delay_minutes=delay_breakdown['air_traffic'],
                            security_delay_minutes=delay_breakdown['security'],
                            mechanical_delay_minutes=delay_breakdown['mechanical'],
                            crew_delay_minutes=delay_breakdown['crew'],
                            
                            # Historical performance
                            route_on_time_percentage=route_on_time_percentage,
                            airline_on_time_percentage=airline_on_time_percentage,
                            time_of_day_delay_factor=time_of_day_factor,
                            day_of_week_delay_factor=day_of_week_factor,
                            seasonal_delay_factor=seasonal_factor,
                            
                            # Current conditions
                            current_weather_delay_risk=flight_data['current_weather_delay_risk'],
                            current_air_traffic_delay_risk=flight_data['current_air_traffic_delay_risk'],
                            current_airport_congestion_level=random.uniform(0.3, 0.8),
                            
                            # Delay reason analysis
                            primary_delay_reason=analysis.primary_reason.value,
                            primary_delay_reason_percentage=analysis.primary_percentage,
                            secondary_delay_reason=analysis.secondary_reason.value if analysis.secondary_reason else None,
                            delay_reason_confidence=analysis.confidence
                        )
                        
                        db.session.add(flight)
                        flights_this_day += 1
                        total_flights_generated += 1
                
                db.session.commit()
                print(f"✅ Generated {flights_this_day} flights for {flight_date}")
            
            print(f"🎉 Generated {total_flights_generated} comprehensive flights!")
            
            # Show statistics
            self._show_generation_statistics()
            
            return total_flights_generated
    
    def _calculate_realistic_delays(self, on_time_rate: float, hour: int, route_data: Dict) -> Dict[str, int]:
        """Calculate realistic delay breakdown"""
        
        delays = {
            'weather': 0,
            'air_traffic': 0,
            'security': 0,
            'mechanical': 0,
            'crew': 0
        }
        
        # Base delay probability based on airline performance
        base_delay_prob = 1 - on_time_rate
        
        # Weather delays
        if random.random() < 0.15:  # 15% chance
            delays['weather'] = random.randint(5, 45)
        
        # Air traffic delays (more likely during peak hours)
        if hour in [7, 8, 9, 17, 18, 19]:  # Peak hours
            if random.random() < 0.25:  # 25% chance during peak
                delays['air_traffic'] = random.randint(5, 30)
        else:
            if random.random() < 0.10:  # 10% chance during off-peak
                delays['air_traffic'] = random.randint(5, 20)
        
        # Security delays
        if random.random() < 0.20:  # 20% chance
            delays['security'] = random.randint(2, 15)
        
        # Mechanical delays (rare but significant)
        if random.random() < 0.05:  # 5% chance
            delays['mechanical'] = random.randint(15, 60)
        
        # Crew delays
        if random.random() < 0.08:  # 8% chance
            delays['crew'] = random.randint(5, 25)
        
        # Adjust based on airline performance
        if on_time_rate < 0.8:  # Poor performing airline
            for key in delays:
                delays[key] = int(delays[key] * 1.2)
        elif on_time_rate > 0.85:  # Good performing airline
            for key in delays:
                delays[key] = int(delays[key] * 0.8)
        
        return delays
    
    def _calculate_time_delay_factor(self, hour: int) -> float:
        """Calculate delay factor based on time of day"""
        if hour in [7, 8, 9, 17, 18, 19]:  # Peak hours
            return random.uniform(1.2, 1.5)
        elif hour in [22, 23, 0, 1, 2, 3, 4, 5]:  # Off-peak hours
            return random.uniform(0.8, 1.0)
        else:  # Regular hours
            return random.uniform(1.0, 1.2)
    
    def _calculate_day_delay_factor(self, weekday: int) -> float:
        """Calculate delay factor based on day of week"""
        if weekday in [4, 5, 6]:  # Weekend (Friday, Saturday, Sunday)
            return random.uniform(1.1, 1.3)
        else:  # Weekdays
            return random.uniform(1.0, 1.1)
    
    def _calculate_seasonal_delay_factor(self, month: int) -> float:
        """Calculate seasonal delay factor"""
        if month in [12, 1, 2]:  # Winter
            return random.uniform(1.1, 1.4)
        elif month in [6, 7, 8]:  # Summer
            return random.uniform(1.0, 1.2)
        else:  # Spring/Fall
            return random.uniform(1.0, 1.1)
    
    def _show_generation_statistics(self):
        """Show statistics about generated flights"""
        with app.app_context():
            total_flights = Flight.query.count()
            delayed_flights = Flight.query.filter(Flight.delay_minutes > 0).count()
            cancelled_flights = Flight.query.filter(Flight.status == 'CANCELLED').count()
            
            print(f"\n📊 Flight Generation Statistics:")
            print(f"   Total flights in database: {total_flights}")
            print(f"   Delayed flights: {delayed_flights}")
            print(f"   Cancelled flights: {cancelled_flights}")
            print(f"   On-time flights: {total_flights - delayed_flights - cancelled_flights}")
            
            # Show delay reason breakdown
            delay_reasons = {}
            flights_with_reasons = Flight.query.filter(Flight.primary_delay_reason.isnot(None)).all()
            
            for flight in flights_with_reasons:
                reason = flight.primary_delay_reason
                delay_reasons[reason] = delay_reasons.get(reason, 0) + 1
            
            if delay_reasons:
                print(f"\n📈 Delay Reason Breakdown:")
                total_with_reasons = sum(delay_reasons.values())
                for reason, count in sorted(delay_reasons.items(), key=lambda x: x[1], reverse=True):
                    percentage = (count / total_with_reasons) * 100
                    icon = self.delay_analyzer.get_reason_icon(DelayReason(reason))
                    print(f"   {icon} {reason}: {count} flights ({percentage:.1f}%)")

def main():
    """Main function to generate more real flights"""
    print("🚀 Generate More Real Flights")
    print("=" * 50)
    
    generator = MoreRealFlightsGenerator()
    
    try:
        flights_generated = generator.generate_comprehensive_flights(days_ahead=3)
        print(f"\n✅ Successfully generated {flights_generated} additional flights!")
        print(f"🌐 Visit http://localhost:8000 to see the expanded flight data")
        
    except Exception as e:
        print(f"\n❌ Error generating flights: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
