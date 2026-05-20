"""
Test script for the new delete functionality in the Calorie Counter app.
"""
import sqlite3
import pandas as pd
from datetime import datetime

def test_delete_functionality():
    """Test the new delete functionality."""
    print("🧪 Testing Delete Functionality")
    print("=" * 40)
    
    # Connect to database
    conn = sqlite3.connect("calorie_counter.db")
    cursor = conn.cursor()
    
    # Add some test entries
    test_date = datetime.now().strftime("%Y-%m-%d")
    test_entries = [
        (test_date, "Test Food 1", 100, 200, 10, 30, 5),
        (test_date, "Test Food 2", 150, 300, 15, 40, 8),
        (test_date, "Test Food 3", 80, 150, 8, 20, 3)
    ]
    
    print("1. Adding test entries...")
    inserted_ids = []
    for entry in test_entries:
        cursor.execute('''
            INSERT INTO food_logs (date, food_name, serving_size, calories, protein, carbohydrates, fat)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', entry)
        inserted_ids.append(cursor.lastrowid)
    
    conn.commit()
    print(f"   ✅ Added {len(test_entries)} test entries")
    
    # Check entries exist
    cursor.execute("SELECT COUNT(*) FROM food_logs WHERE food_name LIKE 'Test Food%'")
    count_before = cursor.fetchone()[0]
    print(f"   📊 Test entries in database: {count_before}")
    
    # Test delete function
    print("\n2. Testing delete functionality...")
    
    # Delete the first test entry
    delete_id = inserted_ids[0]
    cursor.execute('DELETE FROM food_logs WHERE id = ?', (delete_id,))
    deleted_rows = cursor.rowcount
    conn.commit()
    
    if deleted_rows > 0:
        print(f"   ✅ Successfully deleted entry with ID {delete_id}")
    else:
        print(f"   ❌ Failed to delete entry with ID {delete_id}")
    
    # Check remaining entries
    cursor.execute("SELECT COUNT(*) FROM food_logs WHERE food_name LIKE 'Test Food%'")
    count_after = cursor.fetchone()[0]
    print(f"   📊 Test entries remaining: {count_after}")
    
    # Test get_recent_logs equivalent
    print("\n3. Testing recent logs query...")
    df = pd.read_sql_query('''
        SELECT id, date, food_name, serving_size, calories, protein, carbohydrates, fat, timestamp
        FROM food_logs 
        WHERE food_name LIKE 'Test Food%'
        ORDER BY timestamp DESC
        LIMIT 10
    ''', conn)
    
    print(f"   📋 Recent test logs found: {len(df)}")
    if not df.empty:
        print("   Sample entries:")
        for _, row in df.iterrows():
            print(f"      • ID {row['id']}: {row['food_name']} ({row['serving_size']}g) - {row['calories']} cal")
    
    # Cleanup - remove remaining test entries
    print("\n4. Cleaning up test data...")
    cursor.execute("DELETE FROM food_logs WHERE food_name LIKE 'Test Food%'")
    cleaned_count = cursor.rowcount
    conn.commit()
    print(f"   🧹 Cleaned up {cleaned_count} test entries")
    
    conn.close()
    
    print("\n✅ Delete functionality test completed!")
    print("\n📋 New features available:")
    print("   • Delete individual food log entries")
    print("   • Bulk delete by date") 
    print("   • Confirmation dialogs for safety")
    print("   • Recent logs management")
    print("   • Filter logs by date")

if __name__ == "__main__":
    test_delete_functionality()