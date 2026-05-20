import sqlite3
import pandas as pd

def show_indian_foods():
    """Display sample Indian foods from the comprehensive database."""
    conn = sqlite3.connect("calorie_counter.db")
    
    print("🍛 Comprehensive Indian Food Database Loaded!")
    print("=" * 50)
    
    # Get total count
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM food_items")
    total_count = cursor.fetchone()[0]
    print(f"📊 Total food items: {total_count}")
    
    # Show some popular categories
    categories = [
        ("Rice Dishes", "%rice%"),
        ("Dal & Lentils", "%dal%"),
        ("Curry Dishes", "%curry%"),
        ("Bread & Chapati", "%chapati%"),
        ("Biryani", "%biryani%"),
        ("Sweets & Desserts", "%ladoo%"),
        ("Snacks", "%samosa%"),
        ("Beverages", "%tea%")
    ]
    
    for category, pattern in categories:
        df = pd.read_sql_query(f"""
            SELECT name, calories, protein, carbohydrates, fat 
            FROM food_items 
            WHERE name LIKE '{pattern}' 
            ORDER BY calories DESC 
            LIMIT 5
        """, conn)
        
        if not df.empty:
            print(f"\n🥘 {category}:")
            for _, row in df.iterrows():
                print(f"   • {row['name']}: {row['calories']:.1f} cal, {row['protein']:.1f}g protein")
    
    # Show high-protein foods
    print(f"\n💪 High-Protein Indian Foods (Top 10):")
    df_protein = pd.read_sql_query("""
        SELECT name, calories, protein, carbohydrates, fat 
        FROM food_items 
        ORDER BY protein DESC 
        LIMIT 10
    """, conn)
    
    for _, row in df_protein.iterrows():
        print(f"   • {row['name']}: {row['protein']:.1f}g protein, {row['calories']:.1f} cal")
    
    # Show low-calorie options
    print(f"\n🥗 Low-Calorie Options (Under 50 calories):")
    df_low_cal = pd.read_sql_query("""
        SELECT name, calories, protein, carbohydrates, fat 
        FROM food_items 
        WHERE calories < 50 
        ORDER BY calories ASC 
        LIMIT 10
    """, conn)
    
    for _, row in df_low_cal.iterrows():
        print(f"   • {row['name']}: {row['calories']:.1f} cal, {row['protein']:.1f}g protein")
    
    conn.close()
    print(f"\n✅ Your calorie counter now has access to {total_count} Indian food items!")

if __name__ == "__main__":
    show_indian_foods()