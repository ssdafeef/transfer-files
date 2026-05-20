"""
Database migration script to add support for dual data sources (per serving vs per gram).
"""
import sqlite3
import pandas as pd

def migrate_database():
    """Migrate existing database to support dual data sources."""
    print("🔄 Migrating Database for Dual Data Source Support")
    print("=" * 50)
    
    conn = sqlite3.connect("calorie_counter.db")
    cursor = conn.cursor()
    
    # Check if data_type column exists in food_items
    cursor.execute("PRAGMA table_info(food_items)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'data_type' not in columns:
        print("Adding data_type column to food_items table...")
        cursor.execute("ALTER TABLE food_items ADD COLUMN data_type TEXT DEFAULT 'per_serving'")
        cursor.execute("UPDATE food_items SET data_type = 'per_serving' WHERE data_type IS NULL")
        print("✅ Updated food_items table")
    else:
        print("✅ food_items table already has data_type column")
    
    # Check if data_source column exists in food_logs
    cursor.execute("PRAGMA table_info(food_logs)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'data_source' not in columns:
        print("Adding data_source column to food_logs table...")
        cursor.execute("ALTER TABLE food_logs ADD COLUMN data_source TEXT DEFAULT 'per_serving'")
        cursor.execute("UPDATE food_logs SET data_source = 'per_serving' WHERE data_source IS NULL")
        print("✅ Updated food_logs table")
    else:
        print("✅ food_logs table already has data_source column")
    
    # Create food_items_per_gram table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS food_items_per_gram (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            calories REAL NOT NULL,
            protein REAL NOT NULL,
            carbohydrates REAL NOT NULL,
            fat REAL NOT NULL,
            data_type TEXT DEFAULT 'per_gram'
        )
    ''')
    print("✅ Created/verified food_items_per_gram table")
    
    conn.commit()
    
    # Show current status
    cursor.execute("SELECT COUNT(*) FROM food_items")
    serving_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM food_items_per_gram")
    gram_count = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM food_logs")
    log_count = cursor.fetchone()[0]
    
    print(f"\n📊 Migration Complete!")
    print(f"   • Per-serving foods: {serving_count}")
    print(f"   • Per-gram foods: {gram_count}")
    print(f"   • Food logs: {log_count}")
    
    conn.close()

if __name__ == "__main__":
    migrate_database()