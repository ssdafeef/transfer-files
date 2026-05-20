import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path
import os

# Configure Streamlit page
st.set_page_config(
    page_title="🍎 Calorie Counter",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Database handler class
class CalorieDatabase:
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
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                data_source TEXT DEFAULT 'per_serving'
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_food_item(self, name, calories, protein, carbs, fat):
        """Add a new food item to the database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO food_items (name, calories, protein, carbohydrates, fat)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, calories, protein, carbs, fat))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        finally:
            conn.close()
    
    def get_all_foods(self, data_type="both"):
        """Get all food items from the database."""
        conn = sqlite3.connect(self.db_path)
        
        if data_type == "per_serving":
            df = pd.read_sql_query("SELECT *, 'per_serving' as source FROM food_items ORDER BY name", conn)
        elif data_type == "per_gram":
            df = pd.read_sql_query("SELECT *, 'per_gram' as source FROM food_items_per_gram ORDER BY name", conn)
        else:  # both
            df_serving = pd.read_sql_query("SELECT *, 'per_serving' as source FROM food_items", conn)
            df_gram = pd.read_sql_query("SELECT *, 'per_gram' as source FROM food_items_per_gram", conn)
            df = pd.concat([df_serving, df_gram], ignore_index=True)
            df = df.sort_values('name')
        
        conn.close()
        return df
    
    def get_food_by_name_and_type(self, name, data_type):
        """Get specific food item by name and data type."""
        conn = sqlite3.connect(self.db_path)
        
        if data_type == "per_serving":
            df = pd.read_sql_query("SELECT * FROM food_items WHERE name = ?", conn, params=(name,))
        else:  # per_gram
            df = pd.read_sql_query("SELECT * FROM food_items_per_gram WHERE name = ?", conn, params=(name,))
        
        conn.close()
        return df.iloc[0] if not df.empty else None
    
    def log_food(self, date, food_name, serving_size, calories, protein, carbs, fat, data_source="per_serving"):
        """Log a food entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO food_logs (date, food_name, serving_size, calories, protein, carbohydrates, fat, data_source)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, food_name, serving_size, calories, protein, carbs, fat, data_source))
        
        conn.commit()
        conn.close()
    
    def get_logs_by_date_range(self, start_date, end_date):
        """Get food logs within a date range."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT * FROM food_logs 
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC, timestamp DESC
        ''', conn, params=(start_date, end_date))
        conn.close()
        return df
    
    def get_nutrition_summary(self, start_date, end_date):
        """Get nutrition summary for a date range."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT date,
                   SUM(calories) as total_calories,
                   SUM(protein) as total_protein,
                   SUM(carbohydrates) as total_carbs,
                   SUM(fat) as total_fat
            FROM food_logs 
            WHERE date BETWEEN ? AND ?
            GROUP BY date
            ORDER BY date DESC
        ''', conn, params=(start_date, end_date))
        conn.close()
        return df
    
    def delete_food_log(self, log_id):
        """Delete a specific food log entry."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM food_logs WHERE id = ?', (log_id,))
        deleted_rows = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        return deleted_rows > 0
    
    def get_recent_logs(self, limit=20):
        """Get recent food logs for management."""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query('''
            SELECT id, date, food_name, serving_size, calories, protein, carbohydrates, fat, timestamp
            FROM food_logs 
            ORDER BY timestamp DESC
            LIMIT ?
        ''', conn, params=(limit,))
        conn.close()
        return df

# Initialize database
@st.cache_resource
def init_db():
    return CalorieDatabase()

# Initialize session state
def init_session_state():
    if 'db' not in st.session_state:
        st.session_state.db = init_db()
    if 'food_added' not in st.session_state:
        st.session_state.food_added = False

def add_food_tab():
    """Add Food tab interface."""
    st.header("🍎 Add Food to Your Daily Intake")
    
    # Data source selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("📊 Select Nutrition Data Source")
    
    with col2:
        data_source = st.selectbox(
            "Data Type",
            ["per_serving", "per_gram", "both"],
            format_func=lambda x: {
                "per_serving": "📏 Per Serving",
                "per_gram": "⚖️ Per Gram", 
                "both": "🔄 Both Sources"
            }[x],
            help="Choose nutrition calculation method"
        )
    
    # Info about data sources
    if data_source == "per_serving":
        st.info("📏 **Per Serving Mode**: Nutrition values are calculated based on typical serving sizes")
    elif data_source == "per_gram":
        st.info("⚖️ **Per Gram Mode**: Nutrition values are calculated per gram for precise measurements")
    else:
        st.info("🔄 **Both Sources**: Choose from foods with different measurement standards")
    
    # Get all available foods based on selection
    foods_df = st.session_state.db.get_all_foods(data_source)
    
    if foods_df.empty:
        st.warning("⚠️ No food items in database for selected data source.")
        
        # Instructions for adding data
        st.markdown("""
        **To add food data:**
        1. **Per Serving**: Place `Indian_Food_Nutrition_Processed.csv` in the project directory
        2. **Per Gram**: Place `Indian_Food_Nutrition_Per_Gram.csv` in the project directory  
        3. Run `python data_importer.py` to import the data
        """)
        
        return
    
    # Food selection form
    with st.form("log_food"):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            # Create food options with source indication
            food_options = []
            food_mapping = {}
            
            for _, row in foods_df.iterrows():
                source_label = "📏" if row['source'] == 'per_serving' else "⚖️"
                display_name = f"{source_label} {row['name']}"
                food_options.append(display_name)
                food_mapping[display_name] = (row['name'], row['source'])
            
            selected_food_display = st.selectbox(
                "Select Food Item",
                options=food_options,
                help="📏 = Per Serving data, ⚖️ = Per Gram data"
            )
            
            # Get actual food name and source
            selected_food, selected_source = food_mapping[selected_food_display]
        
        with col2:
            serving_size = st.number_input(
                "Amount (g)",
                min_value=1.0,
                value=100.0,
                step=1.0,
                help="Enter the amount in grams"
            )
        
        with col3:
            log_date = st.date_input(
                "Date",
                value=datetime.now(),
                help="Select the date for this food entry"
            )
        
        with col4:
            st.write("")  # Spacing
            st.write("")  # Spacing
            log_button = st.form_submit_button("🍽️ Log Food", type="primary")
        
        if log_button and selected_food:
            # Get food details
            food_details = st.session_state.db.get_food_by_name_and_type(selected_food, selected_source)
            
            if food_details is not None:
                # Calculate nutrition based on serving size and data source
                if selected_source == "per_serving":
                    # For per-serving data, treat the database values as per 100g
                    multiplier = serving_size / 100
                    calories = food_details['calories'] * multiplier
                    protein = food_details['protein'] * multiplier
                    carbs = food_details['carbohydrates'] * multiplier
                    fat = food_details['fat'] * multiplier
                else:  # per_gram
                    # For per-gram data, multiply directly by serving size
                    calories = food_details['calories'] * serving_size
                    protein = food_details['protein'] * serving_size
                    carbs = food_details['carbohydrates'] * serving_size
                    fat = food_details['fat'] * serving_size
                
                # Log the food
                st.session_state.db.log_food(
                    str(log_date), selected_food, serving_size,
                    calories, protein, carbs, fat, selected_source
                )
                
                st.session_state.food_added = True
                
                # Show success message with source info
                source_text = "per serving basis" if selected_source == "per_serving" else "per gram basis"
                st.success(f"✅ {selected_food} ({serving_size}g) logged for {log_date} using {source_text}!")
                
                # Show nutrition info
                st.info(f"""
                **Nutrition Added:**
                - 🔥 Calories: {calories:.1f}
                - 🥩 Protein: {protein:.1f}g
                - 🍞 Carbs: {carbs:.1f}g
                - 🧈 Fat: {fat:.1f}g
                - 📊 Source: {source_text}
                """)
    
    # Statistics for current selection
    if not foods_df.empty:
        st.subheader("📈 Available Food Items")
        
        source_counts = foods_df['source'].value_counts()
        col1, col2, col3 = st.columns(3)
        
        with col1:
            per_serving_count = source_counts.get('per_serving', 0)
            st.metric("📏 Per Serving Foods", per_serving_count)
        
        with col2:
            per_gram_count = source_counts.get('per_gram', 0)
            st.metric("⚖️ Per Gram Foods", per_gram_count)
        
        with col3:
            total_count = len(foods_df)
            st.metric("🔢 Total Available", total_count)
        
        # Show sample foods
        with st.expander("🔍 Browse Available Foods"):
            display_df = foods_df[['name', 'calories', 'protein', 'source']].copy()
            display_df['source'] = display_df['source'].map({
                'per_serving': '📏 Per Serving',
                'per_gram': '⚖️ Per Gram'
            })
            display_df = display_df.rename(columns={
                'name': 'Food Name',
                'calories': 'Calories',
                'protein': 'Protein (g)',
                'source': 'Data Source'
            })
            st.dataframe(display_df, width='stretch')

def view_statistics_tab():
    """View Statistics tab interface."""
    st.header("📊 Nutrition Statistics")
    
    # Time range selection
    col1, col2, col3 = st.columns(3)
    
    with col1:
        view_type = st.selectbox(
            "Select Time Range",
            ["Daily", "Weekly", "Monthly"],
            help="Choose the time period for statistics"
        )
    
    # Calculate date range based on selection
    today = datetime.now().date()
    
    if view_type == "Daily":
        start_date = today
        end_date = today
    elif view_type == "Weekly":
        start_date = today - timedelta(days=6)
        end_date = today
    else:  # Monthly
        start_date = today - timedelta(days=29)
        end_date = today
    
    with col2:
        start_date = st.date_input("Start Date", value=start_date)
    
    with col3:
        end_date = st.date_input("End Date", value=end_date)
    
    # Get data
    summary_df = st.session_state.db.get_nutrition_summary(str(start_date), str(end_date))
    logs_df = st.session_state.db.get_logs_by_date_range(str(start_date), str(end_date))
    
    if summary_df.empty:
        st.warning("📭 No food logs found for the selected date range.")
        st.info("💡 Tip: Add some food items in the 'Add Food' tab to see statistics here!")
        return
    
    # Total summary metrics
    total_calories = summary_df['total_calories'].sum()
    total_protein = summary_df['total_protein'].sum()
    total_carbs = summary_df['total_carbs'].sum()
    total_fat = summary_df['total_fat'].sum()
    
    # Display summary cards
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🔥 Total Calories", f"{total_calories:.0f}")
    
    with col2:
        st.metric("🥩 Total Protein", f"{total_protein:.1f}g")
    
    with col3:
        st.metric("🍞 Total Carbs", f"{total_carbs:.1f}g")
    
    with col4:
        st.metric("🧈 Total Fat", f"{total_fat:.1f}g")
    
    # Charts
    if len(summary_df) > 1:
        # Daily nutrition chart
        st.subheader("📈 Daily Nutrition Breakdown")
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=summary_df['date'],
            y=summary_df['total_calories'],
            mode='lines+markers',
            name='Calories',
            line=dict(color='#FF6B6B', width=3)
        ))
        
        fig.update_layout(
            title="Calories Over Time",
            xaxis_title="Date",
            yaxis_title="Calories",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Macronutrient distribution
        st.subheader("🥗 Macronutrient Distribution")
        
        macro_data = {
            'Nutrient': ['Protein', 'Carbohydrates', 'Fat'],
            'Amount (g)': [total_protein, total_carbs, total_fat],
            'Calories': [total_protein * 4, total_carbs * 4, total_fat * 9]
        }
        
        macro_df = pd.DataFrame(macro_data)
        
        fig_pie = px.pie(
            macro_df,
            values='Calories',
            names='Nutrient',
            title="Calorie Distribution by Macronutrient",
            color_discrete_map={
                'Protein': '#FF6B6B',
                'Carbohydrates': '#4ECDC4',
                'Fat': '#45B7D1'
            }
        )
        
        st.plotly_chart(fig_pie, width='stretch')
    
    # Detailed logs table
    st.subheader("🗂️ Detailed Food Logs")
    
    if not logs_df.empty:
        # Format the dataframe for display
        display_df = logs_df.copy()
        display_df['calories'] = display_df['calories'].round(1)
        display_df['protein'] = display_df['protein'].round(1)
        display_df['carbohydrates'] = display_df['carbohydrates'].round(1)
        display_df['fat'] = display_df['fat'].round(1)
        display_df['serving_size'] = display_df['serving_size'].round(0)
        
        # Rename columns for better display
        display_df = display_df.rename(columns={
            'date': 'Date',
            'food_name': 'Food',
            'serving_size': 'Serving (g)',
            'calories': 'Calories',
            'protein': 'Protein (g)',
            'carbohydrates': 'Carbs (g)',
            'fat': 'Fat (g)'
        })
        
        st.dataframe(
            display_df[['Date', 'Food', 'Serving (g)', 'Calories', 'Protein (g)', 'Carbs (g)', 'Fat (g)']],
            width='stretch'
        )
    
    # Daily summary table
    if len(summary_df) > 1:
        st.subheader("📅 Daily Summary")
        
        display_summary = summary_df.copy()
        display_summary['total_calories'] = display_summary['total_calories'].round(1)
        display_summary['total_protein'] = display_summary['total_protein'].round(1)
        display_summary['total_carbs'] = display_summary['total_carbs'].round(1)
        display_summary['total_fat'] = display_summary['total_fat'].round(1)
        
        display_summary = display_summary.rename(columns={
            'date': 'Date',
            'total_calories': 'Calories',
            'total_protein': 'Protein (g)',
            'total_carbs': 'Carbs (g)',
            'total_fat': 'Fat (g)'
        })
        
        st.dataframe(display_summary, width='stretch')

def manage_logs_tab():
    """Manage Food Logs tab interface."""
    st.header("🗂️ Manage Your Food Logs")
    st.markdown("View and manage your logged food entries. You can delete incorrect entries here.")
    
    # Get recent logs
    recent_logs = st.session_state.db.get_recent_logs(50)
    
    if recent_logs.empty:
        st.info("📭 No food logs found. Start logging food in the 'Add Food' tab!")
        return
    
    # Display count
    st.write(f"📊 Showing {len(recent_logs)} most recent food logs")
    
    # Filter options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Date filter
        if len(recent_logs) > 0:
            unique_dates = sorted(recent_logs['date'].unique(), reverse=True)
            selected_date = st.selectbox(
                "Filter by date (optional)",
                options=["All dates"] + list(unique_dates),
                help="Select a specific date to view logs for that day only"
            )
        else:
            selected_date = "All dates"
    
    with col2:
        # Refresh button
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Filter logs by date if selected
    if selected_date != "All dates":
        filtered_logs = recent_logs[recent_logs['date'] == selected_date]
    else:
        filtered_logs = recent_logs
    
    if filtered_logs.empty:
        st.warning(f"No logs found for {selected_date}")
        return
    
    # Display logs with delete options
    st.subheader(f"📋 Food Log Entries{' for ' + selected_date if selected_date != 'All dates' else ''}")
    
    # Create a more detailed display
    for idx, log in filtered_logs.iterrows():
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 1, 2, 1])
            
            with col1:
                st.write(f"**{log['food_name']}**")
                st.caption(f"Date: {log['date']} | Time: {log['timestamp']}")
            
            with col2:
                st.metric("Serving", f"{log['serving_size']:.0f}g")
            
            with col3:
                # Nutrition info in a compact format
                nutrition_text = f"""
                🔥 **{log['calories']:.1f}** cal  
                🥩 **{log['protein']:.1f}g** protein  
                🍞 **{log['carbohydrates']:.1f}g** carbs  
                🧈 **{log['fat']:.1f}g** fat
                """
                st.markdown(nutrition_text)
            
            with col4:
                # Delete button with confirmation
                delete_key = f"delete_{log['id']}"
                if st.button("🗑️ Delete", key=delete_key, type="secondary"):
                    st.session_state[f"confirm_delete_{log['id']}"] = True
                
                # Confirmation dialog
                if st.session_state.get(f"confirm_delete_{log['id']}", False):
                    st.warning("⚠️ Confirm deletion?")
                    col_yes, col_no = st.columns(2)
                    
                    with col_yes:
                        if st.button("✅ Yes", key=f"yes_{log['id']}", type="primary"):
                            success = st.session_state.db.delete_food_log(log['id'])
                            if success:
                                st.success(f"✅ Deleted: {log['food_name']}")
                                # Clear confirmation state
                                if f"confirm_delete_{log['id']}" in st.session_state:
                                    del st.session_state[f"confirm_delete_{log['id']}"]
                                st.rerun()
                            else:
                                st.error("❌ Failed to delete entry")
                    
                    with col_no:
                        if st.button("❌ No", key=f"no_{log['id']}"):
                            # Clear confirmation state
                            if f"confirm_delete_{log['id']}" in st.session_state:
                                del st.session_state[f"confirm_delete_{log['id']}"]
                            st.rerun()
            
            st.divider()
    
    # Bulk operations section
    if len(filtered_logs) > 0:
        with st.expander("🔧 Bulk Operations"):
            st.warning("⚠️ **Danger Zone** - These operations cannot be undone!")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if selected_date != "All dates":
                    if st.button(f"🗑️ Delete All Logs for {selected_date}", type="secondary"):
                        st.session_state['confirm_bulk_delete_date'] = selected_date
                    
                    if st.session_state.get('confirm_bulk_delete_date') == selected_date:
                        st.error(f"⚠️ Delete ALL {len(filtered_logs)} logs for {selected_date}?")
                        col_yes, col_no = st.columns(2)
                        
                        with col_yes:
                            if st.button("✅ Confirm Delete All", type="primary"):
                                # Delete all logs for the date
                                deleted_count = 0
                                for _, log in filtered_logs.iterrows():
                                    if st.session_state.db.delete_food_log(log['id']):
                                        deleted_count += 1
                                
                                st.success(f"✅ Deleted {deleted_count} logs for {selected_date}")
                                if 'confirm_bulk_delete_date' in st.session_state:
                                    del st.session_state['confirm_bulk_delete_date']
                                st.rerun()
                        
                        with col_no:
                            if st.button("❌ Cancel"):
                                if 'confirm_bulk_delete_date' in st.session_state:
                                    del st.session_state['confirm_bulk_delete_date']
                                st.rerun()
            
            with col2:
                st.info("💡 **Tip**: Use individual delete buttons for single entries, or filter by date for bulk operations.")
    
    # Summary statistics for current view
    if len(filtered_logs) > 0:
        st.subheader("📈 Summary for Current View")
        
        total_entries = len(filtered_logs)
        total_calories = filtered_logs['calories'].sum()
        total_protein = filtered_logs['protein'].sum()
        total_carbs = filtered_logs['carbohydrates'].sum()
        total_fat = filtered_logs['fat'].sum()
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("📊 Entries", total_entries)
        with col2:
            st.metric("🔥 Calories", f"{total_calories:.0f}")
        with col3:
            st.metric("🥩 Protein", f"{total_protein:.1f}g")
        with col4:
            st.metric("🍞 Carbs", f"{total_carbs:.1f}g")
        with col5:
            st.metric("🧈 Fat", f"{total_fat:.1f}g")

def main():
    """Main application function."""
    # Initialize session state
    init_session_state()
    
    # App header
    st.title("🍎 Calorie Counter App")
    st.markdown("Track your daily nutrition intake and monitor your progress!")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🍽️ Add Food", "📊 View Statistics", "🗂️ Manage Logs"])
    
    with tab1:
        add_food_tab()
    
    with tab2:
        view_statistics_tab()
    
    with tab3:
        manage_logs_tab()
    
    # Sidebar info
    with st.sidebar:
        st.header("ℹ️ App Info")
        st.info("""
        **How to use:**
        1. Add food items in the 'Add Food' tab
        2. View your nutrition statistics in the 'View Statistics' tab
        3. Manage logged entries in the 'Manage Logs' tab
        4. Track your progress over time
        
        **Features:**
        - Daily food logging
        - Nutrition tracking
        - Visual charts
        - Historical data
        - Delete/edit logged entries
        """)
        
        # Database stats
        foods_count = len(st.session_state.db.get_all_foods())
        logs_count = len(st.session_state.db.get_logs_by_date_range("1900-01-01", "2100-01-01"))
        
        st.metric("Food Items in Database", foods_count)
        st.metric("Total Food Logs", logs_count)

if __name__ == "__main__":
    main()