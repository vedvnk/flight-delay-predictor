#!/usr/bin/env python3
"""
Add Global Airports
==================

This script adds major global airports to the database with their real coordinates,
timezones, and other information.
"""

import sys
import os
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from app import app
from models import db, Airport

def add_global_airports():
    """Add major global airports to the database"""
    
    # Comprehensive list of major global airports with real data
    global_airports_data = [
        # North America
        {'iata': 'ATL', 'icao': 'KATL', 'name': 'Hartsfield-Jackson Atlanta International Airport', 'city': 'Atlanta', 'state': 'Georgia', 'country': 'United States', 'lat': 33.6407, 'lon': -84.4277, 'timezone': 'America/New_York'},
        {'iata': 'LAX', 'icao': 'KLAX', 'name': 'Los Angeles International Airport', 'city': 'Los Angeles', 'state': 'California', 'country': 'United States', 'lat': 33.9425, 'lon': -118.4081, 'timezone': 'America/Los_Angeles'},
        {'iata': 'ORD', 'icao': 'KORD', 'name': 'Chicago O\'Hare International Airport', 'city': 'Chicago', 'state': 'Illinois', 'country': 'United States', 'lat': 41.9786, 'lon': -87.9048, 'timezone': 'America/Chicago'},
        {'iata': 'DFW', 'icao': 'KDFW', 'name': 'Dallas/Fort Worth International Airport', 'city': 'Dallas', 'state': 'Texas', 'country': 'United States', 'lat': 32.8968, 'lon': -97.0380, 'timezone': 'America/Chicago'},
        {'iata': 'DEN', 'icao': 'KDEN', 'name': 'Denver International Airport', 'city': 'Denver', 'state': 'Colorado', 'country': 'United States', 'lat': 39.8561, 'lon': -104.6737, 'timezone': 'America/Denver'},
        {'iata': 'JFK', 'icao': 'KJFK', 'name': 'John F. Kennedy International Airport', 'city': 'New York', 'state': 'New York', 'country': 'United States', 'lat': 40.6413, 'lon': -73.7781, 'timezone': 'America/New_York'},
        {'iata': 'LAS', 'icao': 'KLAS', 'name': 'Harry Reid International Airport', 'city': 'Las Vegas', 'state': 'Nevada', 'country': 'United States', 'lat': 36.0840, 'lon': -115.1537, 'timezone': 'America/Los_Angeles'},
        {'iata': 'SEA', 'icao': 'KSEA', 'name': 'Seattle-Tacoma International Airport', 'city': 'Seattle', 'state': 'Washington', 'country': 'United States', 'lat': 47.4502, 'lon': -122.3088, 'timezone': 'America/Los_Angeles'},
        {'iata': 'MIA', 'icao': 'KMIA', 'name': 'Miami International Airport', 'city': 'Miami', 'state': 'Florida', 'country': 'United States', 'lat': 25.7959, 'lon': -80.2870, 'timezone': 'America/New_York'},
        {'iata': 'BOS', 'icao': 'KBOS', 'name': 'Logan International Airport', 'city': 'Boston', 'state': 'Massachusetts', 'country': 'United States', 'lat': 42.3656, 'lon': -71.0096, 'timezone': 'America/New_York'},
        {'iata': 'IAH', 'icao': 'KIAH', 'name': 'George Bush Intercontinental Airport', 'city': 'Houston', 'state': 'Texas', 'country': 'United States', 'lat': 29.9902, 'lon': -95.3368, 'timezone': 'America/Chicago'},
        {'iata': 'MSP', 'icao': 'KMSP', 'name': 'Minneapolis-Saint Paul International Airport', 'city': 'Minneapolis', 'state': 'Minnesota', 'country': 'United States', 'lat': 44.8848, 'lon': -93.2223, 'timezone': 'America/Chicago'},
        {'iata': 'DTW', 'icao': 'KDTW', 'name': 'Detroit Metropolitan Wayne County Airport', 'city': 'Detroit', 'state': 'Michigan', 'country': 'United States', 'lat': 42.2162, 'lon': -83.3554, 'timezone': 'America/New_York'},
        {'iata': 'CLT', 'icao': 'KCLT', 'name': 'Charlotte Douglas International Airport', 'city': 'Charlotte', 'state': 'North Carolina', 'country': 'United States', 'lat': 35.2144, 'lon': -80.9473, 'timezone': 'America/New_York'},
        {'iata': 'PHX', 'icao': 'KPHX', 'name': 'Phoenix Sky Harbor International Airport', 'city': 'Phoenix', 'state': 'Arizona', 'country': 'United States', 'lat': 33.4342, 'lon': -112.0116, 'timezone': 'America/Phoenix'},
        {'iata': 'EWR', 'icao': 'KEWR', 'name': 'Newark Liberty International Airport', 'city': 'Newark', 'state': 'New Jersey', 'country': 'United States', 'lat': 40.6895, 'lon': -74.1745, 'timezone': 'America/New_York'},
        {'iata': 'LGA', 'icao': 'KLGA', 'name': 'LaGuardia Airport', 'city': 'New York', 'state': 'New York', 'country': 'United States', 'lat': 40.7769, 'lon': -73.8740, 'timezone': 'America/New_York'},
        {'iata': 'SFO', 'icao': 'KSFO', 'name': 'San Francisco International Airport', 'city': 'San Francisco', 'state': 'California', 'country': 'United States', 'lat': 37.6213, 'lon': -122.3790, 'timezone': 'America/Los_Angeles'},
        {'iata': 'BWI', 'icao': 'KBWI', 'name': 'Baltimore/Washington International Thurgood Marshall Airport', 'city': 'Baltimore', 'state': 'Maryland', 'country': 'United States', 'lat': 39.1774, 'lon': -76.6684, 'timezone': 'America/New_York'},
        {'iata': 'DCA', 'icao': 'KDCA', 'name': 'Ronald Reagan Washington National Airport', 'city': 'Washington', 'state': 'DC', 'country': 'United States', 'lat': 38.8521, 'lon': -77.0377, 'timezone': 'America/New_York'},
        {'iata': 'MDW', 'icao': 'KMDW', 'name': 'Chicago Midway International Airport', 'city': 'Chicago', 'state': 'Illinois', 'country': 'United States', 'lat': 41.7868, 'lon': -87.7522, 'timezone': 'America/Chicago'},
        
        # Canada
        {'iata': 'YYZ', 'icao': 'CYYZ', 'name': 'Toronto Pearson International Airport', 'city': 'Toronto', 'state': 'Ontario', 'country': 'Canada', 'lat': 43.6777, 'lon': -79.6248, 'timezone': 'America/Toronto'},
        {'iata': 'YVR', 'icao': 'CYVR', 'name': 'Vancouver International Airport', 'city': 'Vancouver', 'state': 'British Columbia', 'country': 'Canada', 'lat': 49.1967, 'lon': -123.1815, 'timezone': 'America/Vancouver'},
        {'iata': 'YUL', 'icao': 'CYUL', 'name': 'Montreal-Pierre Elliott Trudeau International Airport', 'city': 'Montreal', 'state': 'Quebec', 'country': 'Canada', 'lat': 45.4577, 'lon': -73.7499, 'timezone': 'America/Montreal'},
        
        # Mexico
        {'iata': 'MEX', 'icao': 'MMMX', 'name': 'Mexico City International Airport', 'city': 'Mexico City', 'state': 'Mexico City', 'country': 'Mexico', 'lat': 19.4363, 'lon': -99.0721, 'timezone': 'America/Mexico_City'},
        {'iata': 'CUN', 'icao': 'MMUN', 'name': 'Cancún International Airport', 'city': 'Cancún', 'state': 'Quintana Roo', 'country': 'Mexico', 'lat': 21.0365, 'lon': -86.8771, 'timezone': 'America/Cancun'},
        
        # Europe
        {'iata': 'LHR', 'icao': 'EGLL', 'name': 'London Heathrow Airport', 'city': 'London', 'state': 'England', 'country': 'United Kingdom', 'lat': 51.4700, 'lon': -0.4543, 'timezone': 'Europe/London'},
        {'iata': 'CDG', 'icao': 'LFPG', 'name': 'Charles de Gaulle Airport', 'city': 'Paris', 'state': 'Île-de-France', 'country': 'France', 'lat': 49.0097, 'lon': 2.5479, 'timezone': 'Europe/Paris'},
        {'iata': 'AMS', 'icao': 'EHAM', 'name': 'Amsterdam Airport Schiphol', 'city': 'Amsterdam', 'state': 'North Holland', 'country': 'Netherlands', 'lat': 52.3105, 'lon': 4.7683, 'timezone': 'Europe/Amsterdam'},
        {'iata': 'FRA', 'icao': 'EDDF', 'name': 'Frankfurt Airport', 'city': 'Frankfurt', 'state': 'Hesse', 'country': 'Germany', 'lat': 50.0379, 'lon': 8.5622, 'timezone': 'Europe/Berlin'},
        {'iata': 'MAD', 'icao': 'LEMD', 'name': 'Adolfo Suárez Madrid-Barajas Airport', 'city': 'Madrid', 'state': 'Community of Madrid', 'country': 'Spain', 'lat': 40.4983, 'lon': -3.5676, 'timezone': 'Europe/Madrid'},
        {'iata': 'BCN', 'icao': 'LEBL', 'name': 'Barcelona-El Prat Airport', 'city': 'Barcelona', 'state': 'Catalonia', 'country': 'Spain', 'lat': 41.2974, 'lon': 2.0833, 'timezone': 'Europe/Madrid'},
        {'iata': 'FCO', 'icao': 'LIRF', 'name': 'Leonardo da Vinci International Airport', 'city': 'Rome', 'state': 'Lazio', 'country': 'Italy', 'lat': 41.8003, 'lon': 12.2389, 'timezone': 'Europe/Rome'},
        {'iata': 'MXP', 'icao': 'LIMC', 'name': 'Milan Malpensa Airport', 'city': 'Milan', 'state': 'Lombardy', 'country': 'Italy', 'lat': 45.6306, 'lon': 8.7281, 'timezone': 'Europe/Rome'},
        {'iata': 'ZUR', 'icao': 'LSZH', 'name': 'Zurich Airport', 'city': 'Zurich', 'state': 'Zurich', 'country': 'Switzerland', 'lat': 47.4647, 'lon': 8.5492, 'timezone': 'Europe/Zurich'},
        {'iata': 'VIE', 'icao': 'LOWW', 'name': 'Vienna International Airport', 'city': 'Vienna', 'state': 'Vienna', 'country': 'Austria', 'lat': 48.1103, 'lon': 16.5697, 'timezone': 'Europe/Vienna'},
        {'iata': 'BRU', 'icao': 'EBBR', 'name': 'Brussels Airport', 'city': 'Brussels', 'state': 'Brussels-Capital', 'country': 'Belgium', 'lat': 50.9014, 'lon': 4.4844, 'timezone': 'Europe/Brussels'},
        {'iata': 'ARN', 'icao': 'ESSA', 'name': 'Stockholm Arlanda Airport', 'city': 'Stockholm', 'state': 'Stockholm County', 'country': 'Sweden', 'lat': 59.6519, 'lon': 17.9186, 'timezone': 'Europe/Stockholm'},
        {'iata': 'CPH', 'icao': 'EKCH', 'name': 'Copenhagen Airport', 'city': 'Copenhagen', 'state': 'Capital Region', 'country': 'Denmark', 'lat': 55.6180, 'lon': 12.6561, 'timezone': 'Europe/Copenhagen'},
        {'iata': 'OSL', 'icao': 'ENGM', 'name': 'Oslo Airport', 'city': 'Oslo', 'state': 'Oslo', 'country': 'Norway', 'lat': 60.1939, 'lon': 11.1004, 'timezone': 'Europe/Oslo'},
        {'iata': 'HEL', 'icao': 'EFHK', 'name': 'Helsinki Airport', 'city': 'Helsinki', 'state': 'Uusimaa', 'country': 'Finland', 'lat': 60.3172, 'lon': 24.9633, 'timezone': 'Europe/Helsinki'},
        {'iata': 'WAW', 'icao': 'EPWA', 'name': 'Warsaw Chopin Airport', 'city': 'Warsaw', 'state': 'Masovian', 'country': 'Poland', 'lat': 52.1657, 'lon': 20.9671, 'timezone': 'Europe/Warsaw'},
        {'iata': 'PRG', 'icao': 'LKPR', 'name': 'Václav Havel Airport Prague', 'city': 'Prague', 'state': 'Central Bohemian', 'country': 'Czech Republic', 'lat': 50.1008, 'lon': 14.2638, 'timezone': 'Europe/Prague'},
        {'iata': 'BUD', 'icao': 'LHBP', 'name': 'Budapest Ferenc Liszt International Airport', 'city': 'Budapest', 'state': 'Budapest', 'country': 'Hungary', 'lat': 47.4369, 'lon': 19.2556, 'timezone': 'Europe/Budapest'},
        {'iata': 'IST', 'icao': 'LTFM', 'name': 'Istanbul Airport', 'city': 'Istanbul', 'state': 'Istanbul', 'country': 'Turkey', 'lat': 41.2753, 'lon': 28.7519, 'timezone': 'Europe/Istanbul'},
        {'iata': 'ATH', 'icao': 'LGAV', 'name': 'Athens International Airport', 'city': 'Athens', 'state': 'Attica', 'country': 'Greece', 'lat': 37.9364, 'lon': 23.9445, 'timezone': 'Europe/Athens'},
        {'iata': 'LIS', 'icao': 'LPPT', 'name': 'Humberto Delgado Airport', 'city': 'Lisbon', 'state': 'Lisbon', 'country': 'Portugal', 'lat': 38.7742, 'lon': -9.1342, 'timezone': 'Europe/Lisbon'},
        {'iata': 'OPO', 'icao': 'LPPR', 'name': 'Francisco Sá Carneiro Airport', 'city': 'Porto', 'state': 'Porto', 'country': 'Portugal', 'lat': 41.2481, 'lon': -8.6814, 'timezone': 'Europe/Lisbon'},
        {'iata': 'DUB', 'icao': 'EIDW', 'name': 'Dublin Airport', 'city': 'Dublin', 'state': 'Dublin', 'country': 'Ireland', 'lat': 53.4264, 'lon': -6.2499, 'timezone': 'Europe/Dublin'},
        {'iata': 'MAN', 'icao': 'EGCC', 'name': 'Manchester Airport', 'city': 'Manchester', 'state': 'England', 'country': 'United Kingdom', 'lat': 53.3538, 'lon': -2.2750, 'timezone': 'Europe/London'},
        {'iata': 'BHX', 'icao': 'EGBB', 'name': 'Birmingham Airport', 'city': 'Birmingham', 'state': 'England', 'country': 'United Kingdom', 'lat': 52.4539, 'lon': -1.7480, 'timezone': 'Europe/London'},
        {'iata': 'EDI', 'icao': 'EGPH', 'name': 'Edinburgh Airport', 'city': 'Edinburgh', 'state': 'Scotland', 'country': 'United Kingdom', 'lat': 55.9500, 'lon': -3.3725, 'timezone': 'Europe/London'},
        
        # Asia Pacific
        {'iata': 'NRT', 'icao': 'RJAA', 'name': 'Narita International Airport', 'city': 'Tokyo', 'state': 'Chiba', 'country': 'Japan', 'lat': 35.7720, 'lon': 140.3928, 'timezone': 'Asia/Tokyo'},
        {'iata': 'HND', 'icao': 'RJTT', 'name': 'Haneda Airport', 'city': 'Tokyo', 'state': 'Tokyo', 'country': 'Japan', 'lat': 35.5494, 'lon': 139.7798, 'timezone': 'Asia/Tokyo'},
        {'iata': 'ICN', 'icao': 'RKSI', 'name': 'Incheon International Airport', 'city': 'Seoul', 'state': 'Incheon', 'country': 'South Korea', 'lat': 37.4602, 'lon': 126.4407, 'timezone': 'Asia/Seoul'},
        {'iata': 'PEK', 'icao': 'ZBAA', 'name': 'Beijing Capital International Airport', 'city': 'Beijing', 'state': 'Beijing', 'country': 'China', 'lat': 40.0799, 'lon': 116.6031, 'timezone': 'Asia/Shanghai'},
        {'iata': 'PVG', 'icao': 'ZSPD', 'name': 'Shanghai Pudong International Airport', 'city': 'Shanghai', 'state': 'Shanghai', 'country': 'China', 'lat': 31.1434, 'lon': 121.8052, 'timezone': 'Asia/Shanghai'},
        {'iata': 'HKG', 'icao': 'VHHH', 'name': 'Hong Kong International Airport', 'city': 'Hong Kong', 'state': 'Hong Kong', 'country': 'Hong Kong', 'lat': 22.3080, 'lon': 113.9185, 'timezone': 'Asia/Hong_Kong'},
        {'iata': 'SIN', 'icao': 'WSSS', 'name': 'Singapore Changi Airport', 'city': 'Singapore', 'state': 'Singapore', 'country': 'Singapore', 'lat': 1.3644, 'lon': 103.9915, 'timezone': 'Asia/Singapore'},
        {'iata': 'BKK', 'icao': 'VTBS', 'name': 'Suvarnabhumi Airport', 'city': 'Bangkok', 'state': 'Bangkok', 'country': 'Thailand', 'lat': 13.6900, 'lon': 100.7501, 'timezone': 'Asia/Bangkok'},
        {'iata': 'KUL', 'icao': 'WMKK', 'name': 'Kuala Lumpur International Airport', 'city': 'Kuala Lumpur', 'state': 'Selangor', 'country': 'Malaysia', 'lat': 2.7456, 'lon': 101.7099, 'timezone': 'Asia/Kuala_Lumpur'},
        {'iata': 'CGK', 'icao': 'WIII', 'name': 'Soekarno-Hatta International Airport', 'city': 'Jakarta', 'state': 'Jakarta', 'country': 'Indonesia', 'lat': -6.1256, 'lon': 106.6558, 'timezone': 'Asia/Jakarta'},
        {'iata': 'MNL', 'icao': 'RPLL', 'name': 'Ninoy Aquino International Airport', 'city': 'Manila', 'state': 'Metro Manila', 'country': 'Philippines', 'lat': 14.5086, 'lon': 121.0196, 'timezone': 'Asia/Manila'},
        {'iata': 'BNE', 'icao': 'YBBN', 'name': 'Brisbane Airport', 'city': 'Brisbane', 'state': 'Queensland', 'country': 'Australia', 'lat': -27.3842, 'lon': 153.1175, 'timezone': 'Australia/Brisbane'},
        {'iata': 'SYD', 'icao': 'YSSY', 'name': 'Sydney Kingsford Smith Airport', 'city': 'Sydney', 'state': 'New South Wales', 'country': 'Australia', 'lat': -33.9399, 'lon': 151.1753, 'timezone': 'Australia/Sydney'},
        {'iata': 'MEL', 'icao': 'YMML', 'name': 'Melbourne Airport', 'city': 'Melbourne', 'state': 'Victoria', 'country': 'Australia', 'lat': -37.6733, 'lon': 144.8433, 'timezone': 'Australia/Melbourne'},
        {'iata': 'PER', 'icao': 'YPPH', 'name': 'Perth Airport', 'city': 'Perth', 'state': 'Western Australia', 'country': 'Australia', 'lat': -31.9403, 'lon': 115.9669, 'timezone': 'Australia/Perth'},
        {'iata': 'ADL', 'icao': 'YPAD', 'name': 'Adelaide Airport', 'city': 'Adelaide', 'state': 'South Australia', 'country': 'Australia', 'lat': -34.9455, 'lon': 138.5306, 'timezone': 'Australia/Adelaide'},
        {'iata': 'DEL', 'icao': 'VIDP', 'name': 'Indira Gandhi International Airport', 'city': 'New Delhi', 'state': 'Delhi', 'country': 'India', 'lat': 28.5562, 'lon': 77.1000, 'timezone': 'Asia/Kolkata'},
        {'iata': 'BOM', 'icao': 'VABB', 'name': 'Chhatrapati Shivaji Maharaj International Airport', 'city': 'Mumbai', 'state': 'Maharashtra', 'country': 'India', 'lat': 19.0896, 'lon': 72.8656, 'timezone': 'Asia/Kolkata'},
        {'iata': 'BLR', 'icao': 'VOBL', 'name': 'Kempegowda International Airport', 'city': 'Bangalore', 'state': 'Karnataka', 'country': 'India', 'lat': 13.1979, 'lon': 77.7063, 'timezone': 'Asia/Kolkata'},
        {'iata': 'HYD', 'icao': 'VOHS', 'name': 'Rajiv Gandhi International Airport', 'city': 'Hyderabad', 'state': 'Telangana', 'country': 'India', 'lat': 17.2403, 'lon': 78.4294, 'timezone': 'Asia/Kolkata'},
        {'iata': 'CCU', 'icao': 'VECC', 'name': 'Netaji Subhash Chandra Bose International Airport', 'city': 'Kolkata', 'state': 'West Bengal', 'country': 'India', 'lat': 22.6546, 'lon': 88.4467, 'timezone': 'Asia/Kolkata'},
        {'iata': 'MAA', 'icao': 'VOMM', 'name': 'Chennai International Airport', 'city': 'Chennai', 'state': 'Tamil Nadu', 'country': 'India', 'lat': 12.9941, 'lon': 80.1709, 'timezone': 'Asia/Kolkata'},
        
        # Middle East & Africa
        {'iata': 'DXB', 'icao': 'OMDB', 'name': 'Dubai International Airport', 'city': 'Dubai', 'state': 'Dubai', 'country': 'UAE', 'lat': 25.2532, 'lon': 55.3657, 'timezone': 'Asia/Dubai'},
        {'iata': 'AUH', 'icao': 'OMAA', 'name': 'Abu Dhabi International Airport', 'city': 'Abu Dhabi', 'state': 'Abu Dhabi', 'country': 'UAE', 'lat': 24.4330, 'lon': 54.6511, 'timezone': 'Asia/Dubai'},
        {'iata': 'DOH', 'icao': 'OTHH', 'name': 'Hamad International Airport', 'city': 'Doha', 'state': 'Doha', 'country': 'Qatar', 'lat': 25.2611, 'lon': 51.5651, 'timezone': 'Asia/Qatar'},
        {'iata': 'RUH', 'icao': 'OERK', 'name': 'King Khalid International Airport', 'city': 'Riyadh', 'state': 'Riyadh', 'country': 'Saudi Arabia', 'lat': 24.9576, 'lon': 46.6988, 'timezone': 'Asia/Riyadh'},
        {'iata': 'JED', 'icao': 'OEJN', 'name': 'King Abdulaziz International Airport', 'city': 'Jeddah', 'state': 'Makkah', 'country': 'Saudi Arabia', 'lat': 21.6796, 'lon': 39.1565, 'timezone': 'Asia/Riyadh'},
        {'iata': 'CAI', 'icao': 'HECA', 'name': 'Cairo International Airport', 'city': 'Cairo', 'state': 'Cairo', 'country': 'Egypt', 'lat': 30.1219, 'lon': 31.4056, 'timezone': 'Africa/Cairo'},
        {'iata': 'JNB', 'icao': 'FAOR', 'name': 'O. R. Tambo International Airport', 'city': 'Johannesburg', 'state': 'Gauteng', 'country': 'South Africa', 'lat': -26.1367, 'lon': 28.2411, 'timezone': 'Africa/Johannesburg'},
        {'iata': 'CPT', 'icao': 'FACT', 'name': 'Cape Town International Airport', 'city': 'Cape Town', 'state': 'Western Cape', 'country': 'South Africa', 'lat': -33.9648, 'lon': 18.6017, 'timezone': 'Africa/Johannesburg'},
        {'iata': 'LOS', 'icao': 'DNMM', 'name': 'Murtala Muhammed International Airport', 'city': 'Lagos', 'state': 'Lagos', 'country': 'Nigeria', 'lat': 6.5774, 'lon': 3.3212, 'timezone': 'Africa/Lagos'},
        {'iata': 'ADD', 'icao': 'HAAB', 'name': 'Bole International Airport', 'city': 'Addis Ababa', 'state': 'Addis Ababa', 'country': 'Ethiopia', 'lat': 8.9779, 'lon': 38.7993, 'timezone': 'Africa/Addis_Ababa'},
        {'iata': 'NBO', 'icao': 'HKJK', 'name': 'Jomo Kenyatta International Airport', 'city': 'Nairobi', 'state': 'Nairobi', 'country': 'Kenya', 'lat': -1.3192, 'lon': 36.9278, 'timezone': 'Africa/Nairobi'},
        {'iata': 'CMN', 'icao': 'GMMN', 'name': 'Mohammed V International Airport', 'city': 'Casablanca', 'state': 'Casablanca-Settat', 'country': 'Morocco', 'lat': 33.3675, 'lon': -7.5898, 'timezone': 'Africa/Casablanca'},
        {'iata': 'ALG', 'icao': 'DAAG', 'name': 'Houari Boumediene Airport', 'city': 'Algiers', 'state': 'Algiers', 'country': 'Algeria', 'lat': 36.6910, 'lon': 3.2154, 'timezone': 'Africa/Algiers'},
        {'iata': 'TUN', 'icao': 'DTTA', 'name': 'Tunis-Carthage International Airport', 'city': 'Tunis', 'state': 'Tunis', 'country': 'Tunisia', 'lat': 36.8510, 'lon': 10.2272, 'timezone': 'Africa/Tunis'},
        
        # South America
        {'iata': 'GRU', 'icao': 'SBGR', 'name': 'São Paulo-Guarulhos International Airport', 'city': 'São Paulo', 'state': 'São Paulo', 'country': 'Brazil', 'lat': -23.4356, 'lon': -46.4731, 'timezone': 'America/Sao_Paulo'},
        {'iata': 'GIG', 'icao': 'SBGL', 'name': 'Rio de Janeiro-Galeão International Airport', 'city': 'Rio de Janeiro', 'state': 'Rio de Janeiro', 'country': 'Brazil', 'lat': -22.8089, 'lon': -43.2500, 'timezone': 'America/Sao_Paulo'},
        {'iata': 'BSB', 'icao': 'SBBR', 'name': 'Brasília International Airport', 'city': 'Brasília', 'state': 'Distrito Federal', 'country': 'Brazil', 'lat': -15.8692, 'lon': -47.9206, 'timezone': 'America/Sao_Paulo'},
        {'iata': 'SDU', 'icao': 'SBRJ', 'name': 'Santos Dumont Airport', 'city': 'Rio de Janeiro', 'state': 'Rio de Janeiro', 'country': 'Brazil', 'lat': -22.9104, 'lon': -43.1631, 'timezone': 'America/Sao_Paulo'},
        {'iata': 'CGH', 'icao': 'SBSP', 'name': 'São Paulo-Congonhas Airport', 'city': 'São Paulo', 'state': 'São Paulo', 'country': 'Brazil', 'lat': -23.6267, 'lon': -46.6553, 'timezone': 'America/Sao_Paulo'},
        {'iata': 'EZE', 'icao': 'SAEZ', 'name': 'Ezeiza International Airport', 'city': 'Buenos Aires', 'state': 'Buenos Aires', 'country': 'Argentina', 'lat': -34.8222, 'lon': -58.5358, 'timezone': 'America/Argentina/Buenos_Aires'},
        {'iata': 'BUE', 'icao': 'SABE', 'name': 'Jorge Newbery Airfield', 'city': 'Buenos Aires', 'state': 'Buenos Aires', 'country': 'Argentina', 'lat': -34.5592, 'lon': -58.4156, 'timezone': 'America/Argentina/Buenos_Aires'},
        {'iata': 'LIM', 'icao': 'SPIM', 'name': 'Jorge Chávez International Airport', 'city': 'Lima', 'state': 'Lima', 'country': 'Peru', 'lat': -12.0219, 'lon': -77.1143, 'timezone': 'America/Lima'},
        {'iata': 'BOG', 'icao': 'SKBO', 'name': 'El Dorado International Airport', 'city': 'Bogotá', 'state': 'Bogotá', 'country': 'Colombia', 'lat': 4.7016, 'lon': -74.1469, 'timezone': 'America/Bogota'},
        {'iata': 'SCL', 'icao': 'SCEL', 'name': 'Arturo Merino Benítez International Airport', 'city': 'Santiago', 'state': 'Santiago', 'country': 'Chile', 'lat': -33.3928, 'lon': -70.7858, 'timezone': 'America/Santiago'},
        {'iata': 'UIO', 'icao': 'SEQU', 'name': 'Mariscal Sucre International Airport', 'city': 'Quito', 'state': 'Pichincha', 'country': 'Ecuador', 'lat': -0.1411, 'lon': -78.4882, 'timezone': 'America/Guayaquil'},
        {'iata': 'GYE', 'icao': 'SEGU', 'name': 'José Joaquín de Olmedo International Airport', 'city': 'Guayaquil', 'state': 'Guayas', 'country': 'Ecuador', 'lat': -2.1574, 'lon': -79.8836, 'timezone': 'America/Guayaquil'},
        {'iata': 'ASU', 'icao': 'SGAS', 'name': 'Silvio Pettirossi International Airport', 'city': 'Asunción', 'state': 'Asunción', 'country': 'Paraguay', 'lat': -25.2398, 'lon': -57.5191, 'timezone': 'America/Asuncion'},
        {'iata': 'LPB', 'icao': 'SLLP', 'name': 'El Alto International Airport', 'city': 'La Paz', 'state': 'La Paz', 'country': 'Bolivia', 'lat': -16.5133, 'lon': -68.1923, 'timezone': 'America/La_Paz'},
        {'iata': 'VVI', 'icao': 'SLVR', 'name': 'Viru Viru International Airport', 'city': 'Santa Cruz', 'state': 'Santa Cruz', 'country': 'Bolivia', 'lat': -17.6448, 'lon': -63.1354, 'timezone': 'America/La_Paz'},
        {'iata': 'CUR', 'icao': 'TNCC', 'name': 'Hato International Airport', 'city': 'Willemstad', 'state': 'Curaçao', 'country': 'Curaçao', 'lat': 12.1889, 'lon': -68.9598, 'timezone': 'America/Curacao'},
        {'iata': 'POS', 'icao': 'TTPP', 'name': 'Piarco International Airport', 'city': 'Port of Spain', 'state': 'Port of Spain', 'country': 'Trinidad and Tobago', 'lat': 10.5953, 'lon': -61.3372, 'timezone': 'America/Port_of_Spain'},
    ]
    
    with app.app_context():
        added_count = 0
        skipped_count = 0
        
        for airport_data in global_airports_data:
            # Check if airport already exists
            existing_airport = Airport.query.filter_by(iata_code=airport_data['iata']).first()
            
            if existing_airport:
                print(f"⚠️  Airport {airport_data['iata']} already exists, skipping...")
                skipped_count += 1
                continue
            
            try:
                airport = Airport(
                    iata_code=airport_data['iata'],
                    icao_code=airport_data['icao'],
                    name=airport_data['name'],
                    city=airport_data['city'],
                    state=airport_data.get('state'),
                    country=airport_data['country'],
                    latitude=airport_data['lat'],
                    longitude=airport_data['lon'],
                    timezone=airport_data['timezone']
                )
                
                db.session.add(airport)
                db.session.commit()
                print(f"✅ Added airport: {airport_data['iata']} - {airport_data['name']}")
                added_count += 1
                
            except Exception as e:
                print(f"❌ Error adding airport {airport_data['iata']}: {e}")
                db.session.rollback()
        
        print(f"\n🎉 Successfully added {added_count} airports!")
        print(f"📊 Skipped {skipped_count} existing airports")
        
        return added_count

def main():
    """Main function to add global airports"""
    print("🌍 Adding Global Airports")
    print("=" * 50)
    
    try:
        added_count = add_global_airports()
        print(f"\n✅ Successfully added {added_count} global airports!")
        print(f"🌐 Now you can run the flight scraper with comprehensive airport coverage")
        
    except Exception as e:
        print(f"\n❌ Error adding airports: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
