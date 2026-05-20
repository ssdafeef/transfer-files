# 🍎 Calorie Counter App

A comprehensive Streamlit-based calorie tracking application that helps you monitor your daily nutrition intake with an intuitive interface and detailed analytics.

## 🌟 Features

### 🍽️ Add Food Tab
- **Food Database**: Browse and select from a comprehensive database of food items
- **Custom Serving Sizes**: Specify exact serving sizes in grams
- **Date Selection**: Log food for any date (past or present)
- **Real-time Calculations**: Automatic nutrition calculation based on serving size
- **Add New Foods**: Expand the database by adding custom food items
- **Success Feedback**: Visual confirmation when food is logged

### 📊 View Statistics Tab
- **Flexible Time Ranges**: View daily, weekly, or monthly nutrition data
- **Custom Date Ranges**: Select specific start and end dates
- **Comprehensive Metrics**: Track calories, protein, carbohydrates, and fat
- **Visual Charts**: 
  - Daily calorie trends over time
  - Macronutrient distribution pie charts
- **Detailed Tables**: Complete food logs and daily summaries
- **Progress Tracking**: Monitor your nutrition patterns over time

### 🗂️ Manage Logs Tab
- **View Recent Logs**: See your most recent food entries with full details
- **Delete Entries**: Remove incorrect or unwanted log entries
- **Date Filtering**: Filter logs by specific dates for easier management
- **Confirmation Dialogs**: Safety confirmations before deleting entries
- **Bulk Operations**: Delete all logs for a specific date
- **Summary Statistics**: View totals for currently filtered logs
- **Real-time Updates**: Changes reflect immediately across all tabs

### 🎨 User Interface
- **Clean Design**: Modern, intuitive interface with emojis and icons
- **Responsive Layout**: Works well on different screen sizes
- **Real-time Updates**: Data persists across tab navigation
- **Informative Sidebar**: App usage tips and database statistics
- **Error Handling**: Helpful messages for various scenarios
- **Log Management**: Delete and manage food entries with confirmations

## 🚀 Quick Start

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation

1. **Clone or download the project files**
   ```bash
   # Navigate to your project directory
   cd C:\coding\V2CC
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

3. **Import comprehensive food data** (automatic with provided CSV)
   ```bash
   python data_importer.py
   ```
   This will load 1,034+ Indian food items from the CSV database.

4. **Run the application**
   ```bash
   streamlit run calorie_counter.py
   ```

5. **Open in browser**
   - The app will automatically open in your default browser
   - If not, navigate to `http://localhost:8501`

## 📦 Project Structure

```
V2CC/
├── calorie_counter.py      # Main Streamlit application
├── data_importer.py        # Data import utility
├── requirements.txt        # Python dependencies
├── README.md              # This file
└── calorie_counter.db     # SQLite database (created automatically)
```

## 🗄️ Database Schema

The app uses SQLite database with two main tables:

### Food Items Table
- `id`: Primary key
- `name`: Food name (unique)
- `calories`: Calories per 100g
- `protein`: Protein in grams per 100g
- `carbohydrates`: Carbs in grams per 100g
- `fat`: Fat in grams per 100g

### Food Logs Table
- `id`: Primary key
- `date`: Log date
- `food_name`: Name of logged food
- `serving_size`: Serving size in grams
- `calories`: Calculated calories for serving
- `protein`: Calculated protein for serving
- `carbohydrates`: Calculated carbs for serving
- `fat`: Calculated fat for serving
- `timestamp`: When the entry was created

## 🔧 Customization & Extension

The app is designed to be modular and easily extensible:

### Adding New Tabs
```python
# In main() function, add new tab:
tab1, tab2, tab3 = st.tabs(["🍽️ Add Food", "📊 View Statistics", "🎯 Your New Tab"])

with tab3:
    your_new_tab_function()
```

### Adding New Features
- **Goal Setting**: Add daily calorie/macro targets
- **Progress Tracking**: Compare against goals
- **Meal Planning**: Pre-plan meals for future dates
- **Recipe Calculator**: Calculate nutrition for custom recipes
- **Export Data**: Export logs to CSV or PDF reports

### Database Extensions
```python
# Add new columns to existing tables
cursor.execute('ALTER TABLE food_logs ADD COLUMN meal_type TEXT')

# Create new tables for additional features
cursor.execute('''
    CREATE TABLE user_goals (
        id INTEGER PRIMARY KEY,
        date TEXT,
        target_calories REAL,
        target_protein REAL,
        target_carbs REAL,
        target_fat REAL
    )
''')
```

## 📊 Comprehensive Indian Food Database

The app now includes a comprehensive database of **1,034 Indian food items** loaded from the `Indian_Food_Nutrition_Processed.csv` file, featuring:

### 🍛 **Traditional Indian Dishes**
- **Rice Dishes**: Various rice preparations, biryanis, khichdi, pulihora
- **Dal & Lentils**: Multiple varieties of dal, vadas, and lentil-based dishes  
- **Curries**: Paneer, vegetable, and meat curries with detailed nutrition info
- **Bread**: Chapati, roti, parathas, and other Indian breads
- **Snacks**: Samosas, cutlets, namkeens, and traditional snacks
- **Sweets**: Ladoos, halwas, desserts, and festival sweets
- **Beverages**: Traditional drinks, teas, and health beverages

### 🔢 **Detailed Nutrition Information**
Each food item includes:
- **Calories (kcal)** per serving
- **Protein (g)** content
- **Carbohydrates (g)** including complex carbs
- **Fats (g)** including healthy fats
- All values calculated per 100g for easy serving size adjustments

### 🥗 **Variety of Options**
- **High-Protein Foods**: Chicken dishes, lentils, protein supplements
- **Low-Calorie Options**: Light soups, teas, vegetable-based dishes
- **Traditional Favorites**: Regional specialties from across India
- **Modern Fusion**: Contemporary Indian fusion dishes

## 🔍 Usage Tips

1. **Start with Sample Data**: Run `data_importer.py` to populate the database
2. **Accurate Serving Sizes**: Use a kitchen scale for precise measurements
3. **Consistent Logging**: Log food immediately after eating for best results
4. **Regular Review**: Check your statistics weekly to identify patterns
5. **Custom Foods**: Add restaurant meals or homemade dishes to the database
6. **Manage Mistakes**: Use the 'Manage Logs' tab to delete incorrect entries
7. **Date Filtering**: Filter logs by date for easier bulk management
8. **Safety First**: Confirm deletions carefully as they cannot be undone

## 🐛 Troubleshooting

### Common Issues

**"No food items in database"**
- Run `python data_importer.py` to add sample data
- Or manually add food items through the app interface

**Database locked error**
- Close any other instances of the app
- Restart the Streamlit server

**Charts not displaying**
- Ensure you have logged food for multiple days
- Check that the date range includes your logged entries

**Package installation errors**
- Update pip: `python -m pip install --upgrade pip`
- Install packages individually if needed

## 🔄 Data Backup & Recovery

### Backup Your Data
```bash
# Copy the database file
copy calorie_counter.db calorie_counter_backup.db
```

### Restore from Backup
```bash
# Replace current database with backup
copy calorie_counter_backup.db calorie_counter.db
```

## 🤝 Contributing

Feel free to fork this project and submit pull requests for:
- Bug fixes
- New features
- UI improvements
- Additional food data
- Documentation improvements

## 📄 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section above
2. Review the code comments for implementation details
3. Create an issue with detailed description and error messages

---

**Happy tracking! 🎉**

Start your nutrition journey today with this comprehensive calorie counter app.