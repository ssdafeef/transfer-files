"""
Final verification script for the Calorie Counter App with comprehensive Indian food database.
"""
import sqlite3
import pandas as pd
import streamlit
from pathlib import Path

def verify_setup():
    """Verify that everything is set up correctly."""
    print("🍎 Calorie Counter App - Final Verification")
    print("=" * 50)
    
    # Check files
    required_files = [
        "calorie_counter.py",
        "data_importer.py", 
        "Indian_Food_Nutrition_Processed.csv",
        "requirements.txt",
        "README.md"
    ]
    
    print("📁 Checking required files:")
    for file in required_files:
        if Path(file).exists():
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING!")
    
    # Check database
    print("\n🗄️ Checking database:")
    if Path("calorie_counter.db").exists():
        print("   ✅ Database file exists")
        
        conn = sqlite3.connect("calorie_counter.db")
        cursor = conn.cursor()
        
        # Check food_items table
        cursor.execute("SELECT COUNT(*) FROM food_items")
        food_count = cursor.fetchone()[0]
        print(f"   ✅ Food items: {food_count}")
        
        # Check food_logs table  
        cursor.execute("SELECT COUNT(*) FROM food_logs")
        log_count = cursor.fetchone()[0]
        print(f"   ✅ Food logs: {log_count}")
        
        # Sample foods
        cursor.execute("SELECT name FROM food_items ORDER BY RANDOM() LIMIT 3")
        sample_foods = [row[0] for row in cursor.fetchall()]
        print(f"   ✅ Sample foods: {', '.join(sample_foods)}")
        
        conn.close()
    else:
        print("   ❌ Database not found - run data_importer.py")
    
    # Check Python packages
    print("\n📦 Checking Python packages:")
    try:
        import streamlit
        print(f"   ✅ Streamlit {streamlit.__version__}")
    except ImportError:
        print("   ❌ Streamlit not installed")
    
    try:
        import pandas
        print(f"   ✅ Pandas {pandas.__version__}")
    except ImportError:
        print("   ❌ Pandas not installed")
        
    try:
        import plotly
        print(f"   ✅ Plotly {plotly.__version__}")
    except ImportError:
        print("   ❌ Plotly not installed")
    
    # Database statistics
    if Path("calorie_counter.db").exists():
        print("\n📈 Database Statistics:")
        conn = sqlite3.connect("calorie_counter.db")
        
        # Top calorie foods
        df_high_cal = pd.read_sql_query("""
            SELECT name, calories FROM food_items 
            ORDER BY calories DESC LIMIT 3
        """, conn)
        print("   🔥 Highest calorie foods:")
        for _, row in df_high_cal.iterrows():
            print(f"      • {row['name']}: {row['calories']:.1f} cal")
        
        # High protein foods
        df_high_protein = pd.read_sql_query("""
            SELECT name, protein FROM food_items 
            ORDER BY protein DESC LIMIT 3
        """, conn)
        print("   💪 Highest protein foods:")
        for _, row in df_high_protein.iterrows():
            print(f"      • {row['name']}: {row['protein']:.1f}g")
        
        # Low calorie options
        df_low_cal = pd.read_sql_query("""
            SELECT name, calories FROM food_items 
            WHERE calories > 0 AND calories < 50
            ORDER BY calories ASC LIMIT 3
        """, conn)
        print("   🥗 Low calorie options:")
        for _, row in df_low_cal.iterrows():
            print(f"      • {row['name']}: {row['calories']:.1f} cal")
        
        conn.close()
    
    print("\n🚀 Ready to launch!")
    print("   Run: streamlit run calorie_counter.py")
    print("   Or use: .\\run_app.ps1")

if __name__ == "__main__":
    verify_setup()