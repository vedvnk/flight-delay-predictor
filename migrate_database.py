#!/usr/bin/env python3
"""
Database Migration Script
========================

This script migrates the existing database to include new fields for enhanced delay prediction.
"""

import sqlite3
import os
from datetime import datetime

def migrate_database():
    """Migrate the database to add new columns"""
    db_path = 'instance/ontime.db'
    
    if not os.path.exists(db_path):
        print("❌ Database file not found!")
        return False
    
    print("🔄 Starting database migration...")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # List of new columns to add to flights table
        new_columns = [
            ('delay_percentage', 'REAL'),
            ('air_traffic_delay_minutes', 'INTEGER DEFAULT 0'),
            ('weather_delay_minutes', 'INTEGER DEFAULT 0'),
            ('security_delay_minutes', 'INTEGER DEFAULT 0'),
            ('mechanical_delay_minutes', 'INTEGER DEFAULT 0'),
            ('crew_delay_minutes', 'INTEGER DEFAULT 0'),
            ('route_on_time_percentage', 'REAL'),
            ('airline_on_time_percentage', 'REAL'),
            ('time_of_day_delay_factor', 'REAL'),
            ('day_of_week_delay_factor', 'REAL'),
            ('seasonal_delay_factor', 'REAL'),
            ('current_weather_delay_risk', 'REAL'),
            ('current_air_traffic_delay_risk', 'REAL'),
            ('current_airport_congestion_level', 'REAL'),
            ('primary_delay_reason', 'VARCHAR(50)'),
            ('primary_delay_reason_percentage', 'REAL'),
            ('secondary_delay_reason', 'VARCHAR(50)'),
            ('delay_reason_confidence', 'REAL')
        ]
        
        # Check which columns already exist
        cursor.execute("PRAGMA table_info(flights)")
        existing_columns = [row[1] for row in cursor.fetchall()]
        
        # Add new columns that don't exist
        added_count = 0
        for column_name, column_type in new_columns:
            if column_name not in existing_columns:
                try:
                    alter_sql = f"ALTER TABLE flights ADD COLUMN {column_name} {column_type}"
                    cursor.execute(alter_sql)
                    print(f"✅ Added column: {column_name}")
                    added_count += 1
                except sqlite3.Error as e:
                    print(f"❌ Error adding column {column_name}: {e}")
            else:
                print(f"⏭️  Column {column_name} already exists")
        
        conn.commit()
        
        # Update existing records with default values
        if added_count > 0:
            print("🔄 Updating existing records with default values...")
            
            update_sql = """
            UPDATE flights SET
                delay_percentage = CASE 
                    WHEN delay_minutes > 0 AND duration_minutes > 0 
                    THEN (delay_minutes * 100.0 / duration_minutes)
                    ELSE 0 
                END,
                air_traffic_delay_minutes = 0,
                weather_delay_minutes = 0,
                security_delay_minutes = 0,
                mechanical_delay_minutes = 0,
                crew_delay_minutes = 0,
                route_on_time_percentage = 0.8,
                airline_on_time_percentage = 0.8,
                time_of_day_delay_factor = 1.0,
                day_of_week_delay_factor = 1.0,
                seasonal_delay_factor = 1.0,
                current_weather_delay_risk = 0.1,
                current_air_traffic_delay_risk = 0.1,
                current_airport_congestion_level = 0.5
            WHERE delay_percentage IS NULL
            """
            
            cursor.execute(update_sql)
            updated_rows = cursor.rowcount
            print(f"✅ Updated {updated_rows} existing flight records")
            
            conn.commit()
        
        conn.close()
        
        print(f"🎉 Database migration completed successfully!")
        print(f"📊 Added {added_count} new columns")
        return True
        
    except Exception as e:
        print(f"❌ Error during migration: {e}")
        return False

def backup_database():
    """Create a backup of the database before migration"""
    db_path = 'instance/ontime.db'
    backup_path = f'instance/ontime_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.db'
    
    try:
        import shutil
        shutil.copy2(db_path, backup_path)
        print(f"✅ Database backed up to: {backup_path}")
        return True
    except Exception as e:
        print(f"❌ Error creating backup: {e}")
        return False

def main():
    """Main migration function"""
    print("🚀 Database Migration for Enhanced Flight Delay Predictor")
    print("=" * 60)
    
    # Create backup first
    if backup_database():
        # Run migration
        if migrate_database():
            print("\n✅ Migration completed successfully!")
            print("🌐 Your database now supports enhanced delay prediction features!")
        else:
            print("\n❌ Migration failed!")
    else:
        print("\n❌ Could not create backup. Migration aborted for safety.")

if __name__ == "__main__":
    main()
