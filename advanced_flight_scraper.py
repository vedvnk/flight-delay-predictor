#!/usr/bin/env python3
"""
Advanced Flight Scraper for ORD
===============================

This scraper uses multiple techniques to get more flight data:
1. Multiple data sources (FlightRadar24, FlightAware, etc.)
2. Different parsing strategies
3. API endpoints where available
4. More aggressive scraping techniques
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
from datetime import datetime, timedelta
import json
import re
from urllib.parse import urljoin, urlparse

class AdvancedFlightScraper:
    def __init__(self, airport_code="KORD"):
        self.airport_code = airport_code
        self.session = requests.Session()
        
        # More realistic headers to avoid blocking
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0',
        }
        
        self.session.headers.update(self.headers)
        
    def scrape_flightradar24_advanced(self):
        """Advanced FlightRadar24 scraping with multiple techniques."""
        flights = []
        
        try:
            # Try the main arrivals page
            url = f"https://www.flightradar24.com/data/airports/{self.airport_code}/arrivals"
            print(f"🔍 Scraping FlightRadar24: {url}")
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try multiple parsing strategies
                flights.extend(self._parse_flightradar24_table(soup))
                flights.extend(self._parse_flightradar24_divs(soup))
                flights.extend(self._parse_flightradar24_json(soup))
                
                print(f"✅ FlightRadar24: Found {len(flights)} flights")
            else:
                print(f"❌ FlightRadar24: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ FlightRadar24 error: {e}")
            
        return flights
    
    def scrape_flightaware(self):
        """Scrape FlightAware arrivals."""
        flights = []
        
        try:
            # FlightAware arrivals page
            url = f"https://flightaware.com/live/airport/{self.airport_code}/arrivals"
            print(f"🔍 Scraping FlightAware: {url}")
            
            # Add FlightAware specific headers
            headers = self.headers.copy()
            headers['Referer'] = 'https://flightaware.com/'
            
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                flights.extend(self._parse_flightaware(soup))
                print(f"✅ FlightAware: Found {len(flights)} flights")
            else:
                print(f"❌ FlightAware: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ FlightAware error: {e}")
            
        return flights
    
    def scrape_flightstats(self):
        """Scrape FlightStats API if available."""
        flights = []
        
        try:
            # Try FlightStats API endpoints
            api_urls = [
                f"https://api.flightstats.com/flex/flightstatus/rest/v2/json/airport/status/{self.airport_code}/arr/{datetime.now().strftime('%Y/%m/%d')}",
                f"https://api.flightstats.com/flex/flightstatus/rest/v2/json/airport/status/{self.airport_code}/dep/{datetime.now().strftime('%Y/%m/%d')}"
            ]
            
            for url in api_urls:
                print(f"🔍 Trying FlightStats API: {url}")
                response = self.session.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    flights.extend(self._parse_flightstats_api(data))
                    print(f"✅ FlightStats API: Found {len(flights)} flights")
                    break
                    
        except Exception as e:
            print(f"❌ FlightStats error: {e}")
            
        return flights
    
    def scrape_airport_official(self):
        """Try to scrape official airport website."""
        flights = []
        
        try:
            # Chicago O'Hare official arrivals
            url = "https://www.flychicago.com/ohare/flights/arrivals"
            print(f"🔍 Scraping Official ORD: {url}")
            
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                flights.extend(self._parse_official_ord(soup))
                print(f"✅ Official ORD: Found {len(flights)} flights")
            else:
                print(f"❌ Official ORD: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Official ORD error: {e}")
            
        return flights
    
    def _parse_flightradar24_table(self, soup):
        """Parse FlightRadar24 table format."""
        flights = []
        
        # Look for data tables
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')[1:]  # Skip header
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 6:
                    try:
                        flight_data = {
                            'flight_number': self._clean_text(cells[0].get_text()),
                            'airline': self._clean_text(cells[1].get_text()),
                            'origin': self._clean_text(cells[2].get_text()),
                            'scheduled_arrival': self._clean_text(cells[3].get_text()),
                            'actual_arrival': self._clean_text(cells[4].get_text()),
                            'status': self._clean_text(cells[5].get_text()),
                            'source': 'FlightRadar24_table'
                        }
                        if flight_data['flight_number'] and flight_data['flight_number'] != 'Flight':
                            flights.append(flight_data)
                    except:
                        continue
                        
        return flights
    
    def _parse_flightradar24_divs(self, soup):
        """Parse FlightRadar24 div-based format."""
        flights = []
        
        # Look for flight cards/divs
        flight_divs = soup.find_all('div', class_=re.compile(r'flight|row|card'))
        for div in flight_divs:
            try:
                # Extract flight information from div structure
                flight_elements = div.find_all(['span', 'div'], class_=re.compile(r'flight|airline|time|status'))
                
                if len(flight_elements) >= 4:
                    flight_data = {
                        'flight_number': self._extract_flight_number(div),
                        'airline': self._extract_airline(div),
                        'origin': self._extract_origin(div),
                        'scheduled_arrival': self._extract_scheduled_time(div),
                        'actual_arrival': self._extract_actual_time(div),
                        'status': self._extract_status(div),
                        'source': 'FlightRadar24_divs'
                    }
                    if flight_data['flight_number']:
                        flights.append(flight_data)
            except:
                continue
                
        return flights
    
    def _parse_flightradar24_json(self, soup):
        """Try to extract JSON data from FlightRadar24."""
        flights = []
        
        try:
            # Look for script tags with JSON data
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'flights' in script.string:
                    # Try to extract JSON
                    json_match = re.search(r'({.*"flights".*})', script.string)
                    if json_match:
                        try:
                            data = json.loads(json_match.group(1))
                            flights.extend(self._parse_json_flights(data))
                        except:
                            continue
        except:
            pass
            
        return flights
    
    def _parse_flightaware(self, soup):
        """Parse FlightAware format."""
        flights = []
        
        # FlightAware specific parsing
        flight_rows = soup.find_all('tr', class_=re.compile(r'flight|row'))
        for row in flight_rows:
            try:
                cells = row.find_all('td')
                if len(cells) >= 6:
                    flight_data = {
                        'flight_number': self._clean_text(cells[0].get_text()),
                        'airline': self._clean_text(cells[1].get_text()),
                        'origin': self._clean_text(cells[2].get_text()),
                        'scheduled_arrival': self._clean_text(cells[3].get_text()),
                        'actual_arrival': self._clean_text(cells[4].get_text()),
                        'status': self._clean_text(cells[5].get_text()),
                        'source': 'FlightAware'
                    }
                    if flight_data['flight_number']:
                        flights.append(flight_data)
            except:
                continue
                
        return flights
    
    def _parse_flightstats_api(self, data):
        """Parse FlightStats API response."""
        flights = []
        
        try:
            if 'flightStatuses' in data:
                for flight in data['flightStatuses']:
                    flight_data = {
                        'flight_number': flight.get('flightNumber', ''),
                        'airline': flight.get('carrierFsCode', ''),
                        'origin': flight.get('departureAirportFsCode', ''),
                        'scheduled_arrival': flight.get('arrivalDate', {}).get('dateLocal', ''),
                        'actual_arrival': flight.get('operationalTimes', {}).get('actualGateArrival', {}).get('dateLocal', ''),
                        'status': flight.get('status', ''),
                        'source': 'FlightStats_API'
                    }
                    if flight_data['flight_number']:
                        flights.append(flight_data)
        except:
            pass
            
        return flights
    
    def _parse_official_ord(self, soup):
        """Parse official ORD website."""
        flights = []
        
        # Official ORD specific parsing
        flight_sections = soup.find_all(['div', 'section'], class_=re.compile(r'flight|arrival'))
        for section in flight_sections:
            try:
                flight_data = {
                    'flight_number': self._extract_flight_number(section),
                    'airline': self._extract_airline(section),
                    'origin': self._extract_origin(section),
                    'scheduled_arrival': self._extract_scheduled_time(section),
                    'actual_arrival': self._extract_actual_time(section),
                    'status': self._extract_status(section),
                    'source': 'Official_ORD'
                }
                if flight_data['flight_number']:
                    flights.append(flight_data)
            except:
                continue
                
        return flights
    
    def _extract_flight_number(self, element):
        """Extract flight number from element."""
        text = element.get_text()
        flight_match = re.search(r'([A-Z]{2,3}\s?\d{3,4})', text)
        return flight_match.group(1).strip() if flight_match else ''
    
    def _extract_airline(self, element):
        """Extract airline from element."""
        # Look for airline codes or names
        airline_patterns = [
            r'([A-Z]{2,3})\s?\d{3,4}',  # Airline code + flight number
            r'(United|Delta|American|Southwest|JetBlue|Spirit|Frontier|Alaska)',
        ]
        
        text = element.get_text()
        for pattern in airline_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        return ''
    
    def _extract_origin(self, element):
        """Extract origin airport from element."""
        # Look for airport codes
        airport_match = re.search(r'([A-Z]{3})', element.get_text())
        return airport_match.group(1) if airport_match else 'Unknown'
    
    def _extract_scheduled_time(self, element):
        """Extract scheduled time from element."""
        time_match = re.search(r'(\d{1,2}:\d{2})', element.get_text())
        return time_match.group(1) if time_match else 'Unknown'
    
    def _extract_actual_time(self, element):
        """Extract actual time from element."""
        # Look for actual/estimated times
        times = re.findall(r'(\d{1,2}:\d{2})', element.get_text())
        return times[1] if len(times) > 1 else 'Unknown'
    
    def _extract_status(self, element):
        """Extract flight status from element."""
        text = element.get_text().lower()
        if 'delayed' in text:
            return 'Delayed'
        elif 'boarding' in text:
            return 'Boarding'
        elif 'landed' in text:
            return 'Landed'
        elif 'on time' in text:
            return 'On Time'
        else:
            return 'Unknown'
    
    def _parse_json_flights(self, data):
        """Parse JSON flight data."""
        flights = []
        
        try:
            if 'flights' in data:
                for flight in data['flights']:
                    flight_data = {
                        'flight_number': flight.get('flight', ''),
                        'airline': flight.get('airline', ''),
                        'origin': flight.get('from', ''),
                        'scheduled_arrival': flight.get('scheduled', ''),
                        'actual_arrival': flight.get('actual', ''),
                        'status': flight.get('status', ''),
                        'source': 'JSON_data'
                    }
                    if flight_data['flight_number']:
                        flights.append(flight_data)
        except:
            pass
            
        return flights
    
    def _clean_text(self, text):
        """Clean and normalize text."""
        if not text:
            return ''
        return re.sub(r'\s+', ' ', text.strip())
    
    def scrape_all_sources(self):
        """Scrape from all available sources."""
        all_flights = []
        
        print("🚀 Advanced Flight Scraping - Multiple Sources")
        print("=" * 60)
        
        # Try all sources
        sources = [
            self.scrape_flightradar24_advanced,
            self.scrape_flightaware,
            self.scrape_flightstats,
            self.scrape_airport_official,
        ]
        
        for source_func in sources:
            try:
                flights = source_func()
                all_flights.extend(flights)
                
                # Add delay between requests
                time.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(f"❌ Source error: {e}")
                continue
        
        # Remove duplicates
        unique_flights = self._remove_duplicates(all_flights)
        
        print(f"\n📊 Total flights found: {len(unique_flights)}")
        print(f"📊 Unique flights: {len(unique_flights)}")
        
        return unique_flights
    
    def _remove_duplicates(self, flights):
        """Remove duplicate flights based on flight number."""
        seen = set()
        unique_flights = []
        
        for flight in flights:
            flight_key = flight['flight_number'].upper()
            if flight_key not in seen and flight_key:
                seen.add(flight_key)
                unique_flights.append(flight)
                
        return unique_flights

def main():
    """Main function to run the advanced scraper."""
    scraper = AdvancedFlightScraper("KORD")
    flights = scraper.scrape_all_sources()
    
    if flights:
        # Convert to DataFrame
        df = pd.DataFrame(flights)
        
        # Add timestamp
        df['scraped_at'] = datetime.now().isoformat()
        
        # Clean and sort
        df = df.dropna(subset=['flight_number'])
        df = df.sort_values('flight_number')
        
        print(f"\n📋 Sample flights found:")
        print(df.head(10).to_string(index=False))
        
        # Save to CSV
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'advanced_ord_flights_{timestamp}.csv'
        df.to_csv(filename, index=False)
        print(f"\n💾 Data saved to: {filename}")
        
        return df
    else:
        print("❌ No flights found from any source")
        return pd.DataFrame()

if __name__ == "__main__":
    main()
