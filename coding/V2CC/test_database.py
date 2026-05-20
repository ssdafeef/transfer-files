import sqlite3
import pandas as pd
from datetime import datetime

def test_database():
    """Test database functionality."""
    print("Testing Calorie Counter Database...")
    print("=" * 40)
    
    # Connect to database
    conn = sqlite3.connect("calorie_counter.db")
    
    # Test 1: Check food items
    print("1. Testing food items table:")
    food_df = pd.read_sql_query("SELECT * FROM food_items LIMIT 5", conn)
    print(f"   - Found {len(pd.read_sql_query('SELECT * FROM food_items', conn))} food items")
    print("   - Sample foods:")
    for _, row in food_df.iterrows():
        print(f"     • {row['name']}: {row['calories']} cal, {row['protein']}g protein")
    
    # Test 2: Test logging functionality
    print("\n2. Testing food logging:")
    cursor = conn.cursor()
    
    # Add a test log entry
    test_date = datetime.now().strftime("%Y-%m-%d")
    cursor.execute('''
        INSERT INTO food_logs (date, food_name, serving_size, calories, protein, carbohydrates, fat)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (test_date, "Rice (cooked)", 150, 195, 4.05, 42, 0.45))
    
    conn.commit()
    
    # Check logs
    logs_df = pd.read_sql_query("SELECT * FROM food_logs", conn)
    print(f"   - Total log entries: {len(logs_df)}")
    if len(logs_df) > 0:
        latest_log = logs_df.iloc[-1]
        print(f"   - Latest entry: {latest_log['food_name']} ({latest_log['serving_size']}g) on {latest_log['date']}")
    
    # Test 3: Test statistics query
    print("\n3. Testing statistics functionality:")
    stats_df = pd.read_sql_query('''
        SELECT date,
               SUM(calories) as total_calories,
               SUM(protein) as total_protein,
               SUM(carbohydrates) as total_carbs,
               SUM(fat) as total_fat
        FROM food_logs 
        GROUP BY date
        ORDER BY date DESC
    ''', conn)
    
    if len(stats_df) > 0:
        print(f"   - Statistics available for {len(stats_df)} days")
        for _, row in stats_df.iterrows():
            print(f"     • {row['date']}: {row['total_calories']:.1f} cal, {row['total_protein']:.1f}g protein")
    else:
        print("   - No statistics data (no food logs)")
    
    conn.close()
    print("\n✅ Database tests completed successfully!")

if __name__ == "__main__":
    test_database()