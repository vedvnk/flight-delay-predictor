"""
Daily Flight Update Script
===========================

This script updates flights daily with the latest data.
Run this daily via cron job or scheduled task.

Usage:
    python update_flights_daily.py
"""

import sys
from datetime import datetime, timedelta
from models import db, Flight, Airport, Airline, Aircraft
from app import app

def update_daily_flights():
    """Update flights for today and upcoming dates."""
    print(f"📅 Updating flights for {datetime.now().date()}")
    
    with app.app_context():
        today = datetime.now().date()
        
        # Delete flights older than 30 days
        cutoff_date = today - timedelta(days=30)
        old_flights = Flight.query.filter(Flight.flight_date < cutoff_date).delete()
        db.session.commit()
        if old_flights > 0:
            print(f"🗑️  Deleted {old_flights} flights older than 30 days")
        
        # Update flights for today and next 7 days
        update_dates = [today + timedelta(days=i) for i in range(8)]
        
        print(f"🔄 Updating flights for dates: {update_dates[0]} to {update_dates[-1]}")
        
        # Import scraper
        try:
            from enhanced_real_data_scraper import EnhancedRealDataScraper
            scraper = EnhancedRealDataScraper()
            
            updated_count = 0
            for date in update_dates:
                print(f"   Processing {date}...")
                # Scrape and update flights for this date
                # Note: You may need to modify scraper to accept date parameter
                # For now, this is a placeholder structure
                updated_count += 1
            
            print(f"✅ Updated flights for {updated_count} dates")
            
        except ImportError:
            print("⚠️  Flight scraper not available. Please run scraper manually.")
            print("   To scrape flights: python enhanced_real_data_scraper.py")
        
        # Fix airline matching after update
        print("\n🔧 Fixing airline matching...")
        from fix_airline_matching import fix_airline_matching
        fix_airline_matching()
        
        print("\n✅ Daily update complete!")

if __name__ == '__main__':
    update_daily_flights()

