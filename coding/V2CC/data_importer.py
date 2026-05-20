import pandas as pd
import sqlite3
from pathlib import Path

class DataImporter:
    """Utility class to import food nutrition data into the database."""
    
    def __init__(self, db_path="calorie_counter.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create food_items table (per serving data)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                carbohydrates REAL NOT NULL,
                fat REAL NOT NULL,
                data_type TEXT DEFAULT 'per_serving'
            )
        ''')
        
        # Create food_items_per_gram table (per gram data)
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
        
        # Create food_logs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS food_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                food_name TEXT NOT NULL,
                serving_size REAL NOT NULL,
                calories REAL NOT NULL,
                protein REAL NOT NULL,
                carbohydrates REAL NOT NULL,
                fat REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def import_from_csv(self, csv_file_path, data_type="per_serving"):
        """Import food data from CSV file."""
        try:
            # Read the CSV file
            df = pd.read_csv(csv_file_path)
            
            print(f"Loading data from: {csv_file_path}")
            print(f"Data type: {data_type}")
            print(f"CSV shape: {df.shape}")
            print("CSV Columns:", df.columns.tolist())
            
            # Map the specific columns from the Indian Food Nutrition CSV
            column_mapping = {
                'Dish Name': 'name',
                'Calories (kcal)': 'calories',
                'Protein (g)': 'protein', 
                'Carbohydrates (g)': 'carbohydrates',
                'Fats (g)': 'fat'
            }
            
            # Check if all required columns exist
            missing_cols = [col for col in column_mapping.keys() if col not in df.columns]
            if missing_cols:
                print(f"Missing columns: {missing_cols}")
                return False
            
            # Create a subset with mapped columns
            df_subset = df[list(column_mapping.keys())].copy()
            df_subset = df_subset.rename(columns=column_mapping)
            
            # Clean and convert data
            df_subset['name'] = df_subset['name'].astype(str).str.strip()
            
            # Convert nutrition columns to numeric
            for col in ['calories', 'protein', 'carbohydrates', 'fat']:
                df_subset[col] = pd.to_numeric(df_subset[col], errors='coerce').fillna(0.0)
            
            # Remove rows with missing or empty names
            df_subset = df_subset[df_subset['name'].notna()]
            df_subset = df_subset[df_subset['name'] != '']
            df_subset = df_subset[df_subset['name'] != 'nan']
            
            # Remove duplicates
            df_subset = df_subset.drop_duplicates(subset=['name'])
            
            print(f"Processed {len(df_subset)} valid food items")
            
            # Connect to database and insert data
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Choose the appropriate table based on data type
            if data_type == "per_gram":
                table_name = "food_items_per_gram"
                # Clear existing per-gram data to avoid conflicts
                cursor.execute("DELETE FROM food_items_per_gram")
            else:
                table_name = "food_items"
                # Clear existing per-serving data to avoid conflicts
                cursor.execute("DELETE FROM food_items")
            
            conn.commit()
            
            success_count = 0
            for _, row in df_subset.iterrows():
                try:
                    cursor.execute(f'''
                        INSERT INTO {table_name} (name, calories, protein, carbohydrates, fat, data_type)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (row['name'], row['calories'], row['protein'], row['carbohydrates'], row['fat'], data_type))
                    success_count += 1
                except Exception as e:
                    print(f"Error inserting {row['name']}: {e}")
            
            conn.commit()
            conn.close()
            
            print(f"Successfully imported {success_count} food items as {data_type} data")
            return True
            
        except Exception as e:
            print(f"Error importing CSV data: {e}")
            return False
    
    def add_sample_data(self):
        """Add sample Indian food data to the database."""
        sample_foods = [
            # Food Name, Calories, Protein, Carbs, Fat (per 100g)
            ("Rice (cooked)", 130, 2.7, 28, 0.3),
            ("Chapati (wheat)", 297, 9.6, 58, 3.7),
            ("Dal (cooked)", 116, 9.0, 20, 0.4),
            ("Chicken Curry", 165, 25, 5, 6),
            ("Paneer", 265, 18, 1.2, 20),
            ("Potato (boiled)", 87, 1.9, 20, 0.1),
            ("Onion", 40, 1.1, 9.3, 0.1),
            ("Tomato", 18, 0.9, 3.9, 0.2),
            ("Banana", 89, 1.1, 23, 0.3),
            ("Apple", 52, 0.3, 14, 0.2),
            ("Milk (full fat)", 61, 3.2, 4.8, 3.3),
            ("Yogurt (plain)", 61, 3.5, 4.7, 3.3),
            ("Ghee", 900, 0, 0, 100),
            ("Sugar", 387, 0, 100, 0),
            ("Honey", 304, 0.3, 82, 0),
            ("Almonds", 579, 21, 22, 50),
            ("Cashews", 553, 18, 30, 44),
            ("Lentils (dry)", 353, 25, 63, 1.1),
            ("Chickpeas (cooked)", 164, 8.9, 27, 2.6),
            ("Spinach", 23, 2.9, 3.6, 0.4),
            ("Carrots", 41, 0.9, 10, 0.2),
            ("Cucumber", 16, 0.7, 4, 0.1),
            ("Ginger", 80, 1.8, 18, 0.8),
            ("Garlic", 149, 6.4, 33, 0.5),
            ("Coriander leaves", 23, 2.1, 3.7, 0.5),
            ("Green chilies", 40, 1.9, 9.5, 0.2),
            ("Turmeric powder", 354, 7.8, 65, 10),
            ("Cumin powder", 375, 18, 44, 22),
            ("Red chili powder", 282, 12, 54, 14),
            ("Basmati rice (cooked)", 121, 2.6, 25, 0.4)
        ]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        success_count = 0
        for food_data in sample_foods:
            try:
                cursor.execute('''
                    INSERT OR IGNORE INTO food_items (name, calories, protein, carbohydrates, fat)
                    VALUES (?, ?, ?, ?, ?)
                ''', food_data)
                if cursor.rowcount > 0:
                    success_count += 1
            except Exception as e:
                print(f"Error inserting {food_data[0]}: {e}")
        
        conn.commit()
        conn.close()
        
        print(f"Successfully added {success_count} sample food items")
        return True

def main():
    """Main function to run data import."""
    importer = DataImporter()
    
    print("Calorie Counter - Dual Data Import Utility")
    print("=" * 50)
    
    # Check for the Indian Food Nutrition CSV file (per serving)
    csv_per_serving = "Indian_Food_Nutrition_Processed.csv"
    csv_per_gram = "Indian_Food_Nutrition_Per_Gram.csv"  # New file for per gram data
    
    imported_serving = False
    imported_gram = False
    
    # Import per-serving data
    if Path(csv_per_serving).exists():
        print(f"Found per-serving CSV: {csv_per_serving}")
        print("Importing per-serving Indian food database...")
        success = importer.import_from_csv(csv_per_serving, data_type="per_serving")
        if success:
            print("✅ Per-serving database imported successfully!")
            imported_serving = True
        else:
            print("❌ Error importing per-serving CSV data")
    else:
        print(f"Per-serving CSV not found: {csv_per_serving}")
    
    # Import per-gram data
    if Path(csv_per_gram).exists():
        print(f"\nFound per-gram CSV: {csv_per_gram}")
        print("Importing per-gram Indian food database...")
        success = importer.import_from_csv(csv_per_gram, data_type="per_gram")
        if success:
            print("✅ Per-gram database imported successfully!")
            imported_gram = True
        else:
            print("❌ Error importing per-gram CSV data")
    else:
        print(f"\nPer-gram CSV not found: {csv_per_gram}")
        print("Place your per-gram CSV file in the same directory to enable dual-mode nutrition tracking.")
    
    # Fallback to sample data if nothing was imported
    if not imported_serving and not imported_gram:
        print("\nNo CSV files found, adding sample data...")
        importer.add_sample_data()
    
    print("\nData import completed!")
    
    # Show final statistics
    conn = sqlite3.connect(importer.db_path)
    cursor = conn.cursor()
    
    # Count per-serving items
    cursor.execute("SELECT COUNT(*) FROM food_items")
    serving_count = cursor.fetchone()[0]
    
    # Count per-gram items
    cursor.execute("SELECT COUNT(*) FROM food_items_per_gram")
    gram_count = cursor.fetchone()[0]
    
    print(f"📊 Per-serving food items: {serving_count}")
    print(f"📊 Per-gram food items: {gram_count}")
    print(f"📊 Total food items: {serving_count + gram_count}")
    
    # Show examples from both tables
    if serving_count > 0:
        cursor.execute("SELECT name, calories, protein FROM food_items ORDER BY calories DESC LIMIT 3")
        top_serving = cursor.fetchall()
        print("\n🔥 Top per-serving foods (highest calorie):")
        for food in top_serving:
            print(f"   • {food[0]}: {food[1]:.1f} cal, {food[2]:.1f}g protein (per serving)")
    
    if gram_count > 0:
        cursor.execute("SELECT name, calories, protein FROM food_items_per_gram ORDER BY calories DESC LIMIT 3")
        top_gram = cursor.fetchall()
        print("\n🔥 Top per-gram foods (highest calorie):")
        for food in top_gram:
            print(f"   • {food[0]}: {food[1]:.1f} cal, {food[2]:.1f}g protein (per gram)")
    
    conn.close()

if __name__ == "__main__":
    main()