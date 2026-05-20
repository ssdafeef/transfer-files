"""
AI-Driven Intrusion Detection System (IDS) - Streamlit Dashboard
Professional web interface for monitoring network security threats in real-time
"""

import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import time
import json
import psutil
import os
from pathlib import Path

# Configure page settings with professional theme
st.set_page_config(
    page_title="IDS Security Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional CSS styling
st.markdown("""
<style>
    /* Main app styling */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
    }
    
    /* Header styling */
    .header-container {
        background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .header-title {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
        text-align: center;
    }
    
    .header-subtitle {
        color: #e0e6ed;
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0.5rem;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #2a5298;
        margin-bottom: 1rem;
    }
    
    /* Alert styling */
    .alert-critical {
        background: #fef2f2;
        border: 1px solid #fecaca;
        border-left: 4px solid #dc2626;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(220, 38, 38, 0.1);
        color: #991b1b;
    }
    
    .alert-critical strong {
        color: #dc2626;
        font-weight: bold;
    }
    
    .alert-high {
        background: #fffbeb;
        border: 1px solid #fde68a;
        border-left: 4px solid #f59e0b;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(245, 158, 11, 0.1);
        color: #92400e;
    }
    
    .alert-high strong {
        color: #f59e0b;
        font-weight: bold;
    }
    
    .alert-medium {
        background: #fefce8;
        border: 1px solid #fef08a;
        border-left: 4px solid #eab308;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(234, 179, 8, 0.1);
        color: #a16207;
    }
    
    .alert-medium strong {
        color: #eab308;
        font-weight: bold;
    }
    
    .alert-low {
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-left: 4px solid #10b981;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(16, 185, 129, 0.1);
        color: #065f46;
    }
    
    .alert-low strong {
        color: #10b981;
        font-weight: bold;
    }
    
    /* Status indicators */
    .status-online {
        color: #10b981;
        font-weight: bold;
    }
    
    .status-offline {
        color: #dc2626;
        font-weight: bold;
    }
    
    /* Sidebar styling */
    .sidebar .sidebar-content {
        background: #f8fafc;
    }
    
    /* Custom buttons */
    .stButton > button {
        background: #2a5298;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s;
    }
    
    .stButton > button:hover {
        background: #1e3c72;
        transform: translateY(-2px);
    }
    
    /* Data tables */
    .dataframe {
        border: none !important;
    }
    
    .dataframe th {
        background: #f1f5f9 !important;
        color: #1e293b !important;
        font-weight: bold !important;
    }
    
    /* Charts container */
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    /* Recent alerts container */
    .alerts-container {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin: 1rem 0;
        border: 1px solid #e5e7eb;
    }
    
    /* Alert text improvements */
    .alert-critical .alert-content,
    .alert-high .alert-content,
    .alert-medium .alert-content,
    .alert-low .alert-content {
        line-height: 1.5;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'auto_refresh' not in st.session_state:
    st.session_state.auto_refresh = True
if 'refresh_interval' not in st.session_state:
    st.session_state.refresh_interval = 5
if 'alerts_data' not in st.session_state:
    st.session_state.alerts_data = []
if 'system_status' not in st.session_state:
    st.session_state.system_status = {}

# Helper functions
@st.cache_data(ttl=30)
def get_api_data(endpoint):
    """Fetch data from the IDS API with caching"""
    try:
        response = requests.get(f"http://localhost:5000/{endpoint}", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except requests.exceptions.RequestException:
        return None

def get_system_stats():
    """Get system performance statistics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_usage': cpu_percent,
            'memory_usage': memory.percent,
            'memory_total': memory.total / (1024**3),  # GB
            'memory_used': memory.used / (1024**3),    # GB
            'disk_usage': disk.percent,
            'disk_total': disk.total / (1024**3),      # GB
            'disk_used': disk.used / (1024**3)        # GB
        }
    except:
        return {
            'cpu_usage': 0,
            'memory_usage': 0,
            'memory_total': 0,
            'memory_used': 0,
            'disk_usage': 0,
            'disk_total': 0,
            'disk_used': 0
        }

def check_service_status():
    """Check if required services are running"""
    api_status = get_api_data("health") is not None
    
    # Check if any Python processes are running (for main.py, etc.)
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info['cmdline'] or []
                python_processes.append({
                    'pid': proc.info['pid'],
                    'cmdline': ' '.join(cmdline) if cmdline else 'N/A'
                })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    return {
        'api_server': api_status,
        'python_processes': python_processes
    }

def format_timestamp(timestamp_str):
    """Format timestamp for display"""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except:
        return timestamp_str

def get_severity_color(severity):
    """Get color for severity level"""
    colors = {
        'critical': '#dc2626',
        'high': '#f59e0b',
        'medium': '#f59e0b',
        'low': '#10b981'
    }
    return colors.get(severity.lower(), '#6b7280')

def process_custom_data(data_content):
    """Process custom uploaded data through the IDS system"""
    try:
        # Import required modules for processing
        from dfa_engine import check_all_patterns
        from ai_module import AIDetector
        
        # Initialize processing UI elements
        st.sidebar.info("🔄 Starting data processing...")
        
        # Initialize AI detector
        with st.spinner("Loading AI detector..."):
            ai_detector = AIDetector("models/anomaly_model.pkl")
        
        # Split data into lines
        lines = [line.strip() for line in data_content.splitlines() if line.strip() and not line.strip().startswith('#')]
        
        # Store processing results in session state
        if 'processing_results' not in st.session_state:
            st.session_state.processing_results = []
        
        st.session_state.processing_results = []
        
        # Initialize live processing feed
        if 'live_processing_feed' not in st.session_state:
            st.session_state.live_processing_feed = []
        
        st.session_state.live_processing_feed = []
        
        # Process all lines with enhanced progress tracking
        total_lines = len(lines)
        
        # Always show progress bar for better UX
        st.sidebar.info(f"📊 Processing {total_lines} lines...")
        progress_bar = st.sidebar.progress(0)
        progress_text = st.sidebar.empty()
        
        # Processing statistics
        threats_found = 0
        processed_count = 0
        
        for i, line in enumerate(lines):  # Process ALL lines, no limit
            processed_count += 1
            
            # Run DFA detection
            dfa_detections = check_all_patterns(line)
            
            # Run AI detection  
            ai_anomaly = ai_detector.check_and_log(line)
            
            # Determine severity
            severity = get_severity_level(dfa_detections, ai_anomaly)
            
            # Determine alert type based on actual detections
            if dfa_detections and ai_anomaly:
                alert_type = 'combined'  # Both DFA and AI detected
            elif dfa_detections:
                alert_type = 'dfa'      # Only DFA patterns detected
            elif ai_anomaly:
                alert_type = 'ai'       # Only AI anomaly detected
            else:
                alert_type = 'normal'   # No threats detected
            
            # Store result
            result = {
                'line_number': i + 1,
                'message': line,
                'dfa_detections': dfa_detections,
                'ai_anomaly': ai_anomaly,
                'threat_detected': bool(dfa_detections or ai_anomaly),
                'alert_type': alert_type,
                'severity': severity,
                'timestamp': datetime.now().isoformat()
            }
            
            st.session_state.processing_results.append(result)
            
            # Add to live processing feed if threat detected
            if result['threat_detected']:
                threats_found += 1
                feed_entry = {
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'line': i + 1,
                    'message': line[:60] + '...' if len(line) > 60 else line,
                    'severity': severity,
                    'alert_type': alert_type,
                    'patterns': ', '.join(dfa_detections) if dfa_detections else 'AI Anomaly'
                }
                st.session_state.live_processing_feed.append(feed_entry)
            
            # Send threats to API (only if threats are detected)
            if result['threat_detected']:
                try:
                    requests.post(f"{st.session_state.get('api_url', 'http://localhost:5000')}/alerts", json={
                        'message': result['message'],
                        'alert_type': alert_type,
                        'severity': result['severity'].lower(),
                        'line_number': result['line_number'],
                        'line_content': result['message'],
                        'detected_patterns': result['dfa_detections']
                    }, timeout=5)
                except:
                    pass  # Continue processing even if API is unavailable
            
            # Update progress bar and text
            progress = (i + 1) / total_lines
            progress_bar.progress(progress)
            progress_text.text(f"📈 {processed_count}/{total_lines} processed | 🚨 {threats_found} threats found")
            
            # Small delay to make processing visible (remove in production)
            if total_lines < 100:  # Only for smaller files to show the progress
                time.sleep(0.05)
        
        # Clear progress indicators
        progress_bar.empty()
        progress_text.empty()
        
        st.sidebar.success(f"✅ Processed {len(st.session_state.processing_results)} lines")
        threats = sum(1 for r in st.session_state.processing_results if r['threat_detected'])
        st.sidebar.info(f"🚨 Threats found: {threats}")
        
    except Exception as e:
        st.sidebar.error(f"❌ Processing error: {str(e)}")

def process_sample_data():
    """Process the default sample traffic data"""
    try:
        # Read sample traffic file
        sample_file_path = "data/sample_traffic.txt"
        if Path(sample_file_path).exists():
            with open(sample_file_path, 'r') as f:
                content = f.read()
            process_custom_data(content)
        else:
            st.sidebar.error("❌ Sample traffic file not found")
    except Exception as e:
        st.sidebar.error(f"❌ Error processing sample data: {str(e)}")

def get_severity_level(detections, ai_anomaly):
    """Determine threat severity level based on detections"""
    if not detections and not ai_anomaly:
        return "LOW"
    
    critical_patterns = {"ddos", "malware", "ransomware", "zero-day"}
    high_patterns = {"attack", "bruteforce", "injection", "unauthorized access"}
    medium_patterns = {"scan", "phishing", "session hijacking"}
    
    detected_patterns = set(detections)
    
    if detected_patterns.intersection(critical_patterns) or (ai_anomaly and len(detections) >= 2):
        return "CRITICAL"
    elif detected_patterns.intersection(high_patterns) or (ai_anomaly and detections):
        return "HIGH"
    elif detected_patterns.intersection(medium_patterns) or ai_anomaly:
        return "MEDIUM"
    else:
        return "LOW"

# Header
st.markdown("""
<div class="header-container">
    <h1 class="header-title">🛡️ IDS Security Dashboard</h1>
    <p class="header-subtitle">AI-Driven Intrusion Detection System - Real-time Monitoring & Analytics</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
st.sidebar.title("⚙️ Dashboard Controls")

# Auto-refresh controls
st.sidebar.subheader("🔄 Auto-Refresh")
st.session_state.auto_refresh = st.sidebar.checkbox("Enable Auto-Refresh", value=st.session_state.auto_refresh)
st.session_state.refresh_interval = st.sidebar.slider("Refresh Interval (seconds)", 1, 30, st.session_state.refresh_interval)

if st.sidebar.button("🔄 Manual Refresh"):
    st.cache_data.clear()
    st.rerun()

# Data Input Options
st.sidebar.subheader("📁 Data Input")
data_source = st.sidebar.selectbox("Choose Data Source", [
    "📄 Use Sample Traffic Data",
    "📤 Upload Custom File",
    "🔄 Real-time API Data"
])

# File upload section
uploaded_file = None
custom_data_content = None

if data_source == "📤 Upload Custom File":
    st.sidebar.markdown("""
    **📋 File Format:**
    - Text files (.txt, .log, .csv)
    - One network event per line
    - Comments start with #
    """)
    
    uploaded_file = st.sidebar.file_uploader(
        "Upload Traffic Data File", 
        type=['txt', 'log', 'csv'],
        help="Upload a text file with network traffic data (one entry per line)"
    )
    
    if uploaded_file is not None:
        try:
            # Read uploaded file content
            custom_data_content = uploaded_file.read().decode('utf-8')
            st.sidebar.success(f"✅ File uploaded: {uploaded_file.name}")
            
            # Count non-empty, non-comment lines
            valid_lines = [line for line in custom_data_content.splitlines() 
                          if line.strip() and not line.strip().startswith('#')]
            st.sidebar.info(f"📊 Valid data lines: {len(valid_lines)}")
            
            if len(valid_lines) > 50:
                st.sidebar.warning(f"⚠️ Large file detected. Only first 50 lines will be processed for performance.")
            
        except Exception as e:
            st.sidebar.error(f"❌ Error reading file: {str(e)}")
    else:
        st.sidebar.markdown("""
        **💡 Need example data?**
        """)
        
        # Download sample custom data
        try:
            with open("sample_custom_data.txt", "r") as f:
                sample_content = f.read()
            
            st.sidebar.download_button(
                label="📥 Download Sample File",
                data=sample_content,
                file_name="sample_custom_data.txt",
                mime="text/plain",
                help="Download a sample file to test the upload feature"
            )
        except:
            st.sidebar.info("Sample file: `sample_custom_data.txt`")

elif data_source == "📄 Use Sample Traffic Data":
    st.sidebar.info("📄 Using default sample_traffic.txt")
    st.sidebar.markdown("""
    **Contains:**
    - Normal network traffic
    - Various attack patterns
    - Mixed security scenarios
    - ~80+ realistic examples
    """)
    
elif data_source == "🔄 Real-time API Data":
    st.sidebar.info("🔄 Using live data from API")
    st.sidebar.markdown("""
    **Real-time features:**
    - Live alert updates
    - System monitoring
    - Auto-refresh capability
    """)

# Process uploaded data button
if data_source == "📤 Upload Custom File" and custom_data_content:
    if st.sidebar.button("🔄 Process Uploaded Data"):
        process_custom_data(custom_data_content)

# Quick process sample data button
if data_source == "📄 Use Sample Traffic Data":
    if st.sidebar.button("🔄 Process Sample Data"):
        process_sample_data()

# Navigation
st.sidebar.subheader("📊 Navigation")
page = st.sidebar.selectbox("Select Page", [
    "🏠 Real-time Dashboard",
    "🚨 Alert Management", 
    "📈 System Analytics",
    "� 3D Network Topology",
    "�🌍 Threat Intelligence",
    "🎯 Attack Simulator",
    "🤖 AI Insights",
    "🗂️ Data Processing",
    "⚙️ Settings & Configuration"
])

# System status in sidebar
st.sidebar.subheader("🖥️ System Status")
service_status = check_service_status()

# API Server status
api_status = "🟢 Online" if service_status['api_server'] else "🔴 Offline"
st.sidebar.markdown(f"**API Server:** {api_status}")

# Running processes
if service_status['python_processes']:
    st.sidebar.markdown("**Active Processes:**")
    for proc in service_status['python_processes'][:3]:  # Show first 3
        if any(script in proc['cmdline'] for script in ['main.py', 'api.py', 'kafka_consumer.py']):
            st.sidebar.markdown(f"• PID {proc['pid']}")

# Main content based on selected page
if page == "🏠 Real-time Dashboard":
    # Get latest data
    alerts_data = get_api_data("alerts")
    health_data = get_api_data("health")
    system_stats = get_system_stats()
    
    # Status overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if health_data:
            total_alerts = health_data.get('alerts_count', 0)
            st.metric(
                label="📊 Total Alerts",
                value=total_alerts,
                delta=f"+{total_alerts - st.session_state.get('prev_alerts', 0)}" if total_alerts > st.session_state.get('prev_alerts', 0) else None
            )
            st.session_state.prev_alerts = total_alerts
        else:
            st.metric("📊 Total Alerts", "N/A")
    
    with col2:
        api_status_text = "🟢 Online" if service_status['api_server'] else "🔴 Offline"
        st.metric("🔗 API Status", api_status_text)
    
    with col3:
        st.metric("💻 CPU Usage", f"{system_stats['cpu_usage']:.1f}%")
    
    with col4:
        st.metric("💾 Memory Usage", f"{system_stats['memory_usage']:.1f}%")
    
    # Live Processing Feed and Recent Alerts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("⚡ Live Processing Feed")
        
        # Show live processing feed if available
        if 'live_processing_feed' in st.session_state and st.session_state.live_processing_feed:
            live_feed = st.session_state.live_processing_feed[-10:]  # Last 10 items
            live_feed.reverse()  # Show newest first
            
            st.markdown('<div class="alerts-container">', unsafe_allow_html=True)
            
            for entry in live_feed:
                severity_class = f"alert-{entry['severity'].lower()}"
                st.markdown(f"""
                <div class="{severity_class}" style="margin: 0.3rem 0; padding: 0.8rem;">
                    <div style="margin-bottom: 6px;">
                        <strong>[{entry['timestamp']}]</strong> Line {entry['line']} - <strong>{entry['severity']}</strong>
                    </div>
                    <div style="margin-bottom: 4px; font-size: 0.9em;">
                        {entry['message']}
                    </div>
                    <div style="font-size: 0.8em; opacity: 0.9;">
                        🔍 {entry['alert_type'].upper()} | {entry['patterns']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Auto-refresh button for live feed
            if st.button("🔄 Refresh Live Feed"):
                st.rerun()
        else:
            st.info("🔄 Process data to see live threat detection here")
    
    with col2:
        st.subheader("🚨 Recent API Alerts")
        
        if alerts_data and alerts_data.get('alerts'):
            recent_alerts = alerts_data['alerts'][-10:]  # Last 10 alerts
            recent_alerts.reverse()  # Show newest first
            
            # Container for better styling
            st.markdown('<div class="alerts-container">', unsafe_allow_html=True)
            
            for alert in recent_alerts:
                severity = alert.get('severity', 'medium')
                timestamp = format_timestamp(alert.get('timestamp', ''))
                message = alert.get('message', 'No message')
                patterns = ', '.join(alert.get('detected_patterns', []))
                
                # Alert card with appropriate styling
                alert_class = f"alert-{severity}"
                
                st.markdown(f"""
                <div class="{alert_class}">
                    <div style="margin-bottom: 8px;">
                        <strong>{severity.upper()}</strong> 
                        <span style="float: right; font-size: 0.9em; opacity: 0.8;">{timestamp}</span>
                    </div>
                    <div style="margin-bottom: 6px;">
                        <strong>Message:</strong> <span style="color: #374151;">{message}</span>
                    </div>
                    {'<div style="margin-bottom: 6px;"><strong>Patterns:</strong> <span style="color: #374151;">' + patterns + '</span></div>' if patterns else ''}
                    <div style="font-size: 0.9em;">
                        <strong>Type:</strong> <span style="color: #374151;">{alert.get('alert_type', 'unknown')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)  # Close alerts container
        else:
            st.info("No API alerts available. Make sure the API server is running.")
    
    # Live monitoring section
    st.subheader("📈 System Performance")
    
    # Create performance charts
    col1, col2 = st.columns(2)
    
    with col1:
        # CPU and Memory usage chart
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode = "gauge+number+delta",
            value = system_stats['cpu_usage'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "CPU Usage (%)"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Memory usage chart
        fig = go.Figure()
        fig.add_trace(go.Indicator(
            mode = "gauge+number+delta",
            value = system_stats['memory_usage'],
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Memory Usage (%)"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkgreen"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "yellow"},
                    {'range': [80, 100], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

elif page == "🚨 Alert Management":
    st.subheader("Alert Management & Analysis")
    
    # Get alerts data
    alerts_data = get_api_data("alerts")
    
    if alerts_data and alerts_data.get('alerts'):
        alerts = alerts_data['alerts']
        
        # Alert statistics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_alerts = len(alerts)
            st.metric("Total Alerts", total_alerts)
        
        with col2:
            severity_counts = {}
            for alert in alerts:
                sev = alert.get('severity', 'unknown')
                severity_counts[sev] = severity_counts.get(sev, 0) + 1
            critical_high = severity_counts.get('critical', 0) + severity_counts.get('high', 0)
            st.metric("Critical/High Alerts", critical_high)
        
        with col3:
            recent_alerts = [a for a in alerts if 'timestamp' in a]
            if recent_alerts:
                latest_time = max(recent_alerts, key=lambda x: x['timestamp'])['timestamp']
                st.metric("Latest Alert", format_timestamp(latest_time))
        
        # Filters
        st.subheader("🔍 Filter Alerts")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            severity_filter = st.selectbox("Severity Level", 
                                         ["All"] + list(set(alert.get('severity', '') for alert in alerts)))
        
        with col2:
            alert_type_filter = st.selectbox("Alert Type",
                                           ["All"] + list(set(alert.get('alert_type', '') for alert in alerts)))
        
        with col3:
            pattern_filter = st.selectbox("Pattern",
                                        ["All"] + list(set(pattern for alert in alerts for pattern in alert.get('detected_patterns', []))))
        
        # Apply filters
        filtered_alerts = alerts
        if severity_filter != "All":
            filtered_alerts = [a for a in filtered_alerts if a.get('severity') == severity_filter]
        if alert_type_filter != "All":
            filtered_alerts = [a for a in filtered_alerts if a.get('alert_type') == alert_type_filter]
        if pattern_filter != "All":
            filtered_alerts = [a for a in filtered_alerts if pattern_filter in a.get('detected_patterns', [])]
        
        # Display filtered alerts
        st.subheader(f"📋 Alerts ({len(filtered_alerts)} shown)")
        
        if filtered_alerts:
            # Convert to DataFrame for better display
            df_data = []
            for i, alert in enumerate(filtered_alerts):
                df_data.append({
                    'ID': i,
                    'Timestamp': format_timestamp(alert.get('timestamp', '')),
                    'Severity': alert.get('severity', '').upper(),
                    'Message': alert.get('message', ''),
                    'Type': alert.get('alert_type', ''),
                    'Patterns': ', '.join(alert.get('detected_patterns', [])),
                    'Line': alert.get('line_number', 'N/A')
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Alert details
            if st.checkbox("Show Detailed View"):
                selected_alert = st.selectbox("Select Alert for Details", range(len(filtered_alerts)))
                if selected_alert is not None:
                    alert = filtered_alerts[selected_alert]
                    
                    st.json(alert)
        else:
            st.info("No alerts match the selected filters.")
    
    else:
        st.warning("No alerts available. Make sure the API server is running and there are alerts to display.")

elif page == "📈 System Analytics":
    st.subheader("System Analytics & Performance Metrics")
    
    # Get data for analytics
    alerts_data = get_api_data("alerts")
    system_stats = get_system_stats()
    
    # System performance overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💻 System Resources")
        st.write(f"**CPU Usage:** {system_stats['cpu_usage']:.1f}%")
        st.write(f"**Memory:** {system_stats['memory_used']:.2f} GB / {system_stats['memory_total']:.2f} GB ({system_stats['memory_usage']:.1f}%)")
        st.write(f"**Disk:** {system_stats['disk_used']:.2f} GB / {system_stats['disk_total']:.2f} GB ({system_stats['disk_usage']:.1f}%)")
    
    with col2:
        # System resource usage chart
        fig = go.Figure(data=[
            go.Bar(name='Used', x=['CPU', 'Memory', 'Disk'], 
                  y=[system_stats['cpu_usage'], system_stats['memory_usage'], system_stats['disk_usage']]),
        ])
        fig.update_layout(
            title="Resource Usage (%)",
            yaxis_title="Usage Percentage",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
    
    if alerts_data and alerts_data.get('alerts'):
        alerts = alerts_data['alerts']
        
        # Alert statistics
        st.subheader("🚨 Alert Statistics")
        
        # Severity distribution
        severity_counts = {}
        for alert in alerts:
            sev = alert.get('severity', 'unknown')
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Severity pie chart
            fig = px.pie(
                values=list(severity_counts.values()),
                names=list(severity_counts.keys()),
                title="Alerts by Severity Level",
                color_discrete_map={
                    'critical': '#dc2626',
                    'high': '#f59e0b',
                    'medium': '#f59e0b',
                    'low': '#10b981'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Alert type distribution
            type_counts = {}
            for alert in alerts:
                alert_type = alert.get('alert_type', 'unknown')
                type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
            
            fig = px.bar(
                x=list(type_counts.keys()),
                y=list(type_counts.values()),
                title="Alerts by Detection Type"
            )
            fig.update_layout(xaxis_title="Detection Type", yaxis_title="Count")
            st.plotly_chart(fig, use_container_width=True)
        
        # Pattern analysis
        st.subheader("🔍 Pattern Analysis")
        pattern_counts = {}
        for alert in alerts:
            for pattern in alert.get('detected_patterns', []):
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        if pattern_counts:
            fig = px.bar(
                x=list(pattern_counts.values()),
                y=list(pattern_counts.keys()),
                orientation='h',
                title="Most Detected Patterns"
            )
            fig.update_layout(xaxis_title="Frequency", yaxis_title="Pattern")
            st.plotly_chart(fig, use_container_width=True)
        
        # Timeline analysis
        st.subheader("📅 Alert Timeline")
        
        # Parse timestamps and create timeline
        timeline_data = []
        for alert in alerts:
            try:
                timestamp = alert.get('timestamp', '')
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timeline_data.append({
                    'timestamp': dt,
                    'severity': alert.get('severity', 'unknown'),
                    'message': alert.get('message', '')
                })
            except:
                continue
        
        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            df_timeline = df_timeline.sort_values('timestamp')
            
            fig = px.scatter(
                df_timeline,
                x='timestamp',
                y='severity',
                color='severity',
                title="Alert Timeline",
                hover_data=['message']
            )
            st.plotly_chart(fig, use_container_width=True)

elif page == "🗂️ Data Processing":
    st.subheader("Data Processing & Analysis")
    
    # Current data source info with live processing status
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Selected Data Source", data_source.split()[1] if len(data_source.split()) > 1 else "API")
    
    with col2:
        if data_source == "📤 Upload Custom File" and uploaded_file:
            lines_count = len(custom_data_content.splitlines()) if custom_data_content else 0
            st.metric("File Lines", lines_count)
        elif data_source == "📄 Use Sample Traffic Data":
            try:
                with open("data/sample_traffic.txt", 'r') as f:
                    lines_count = len([line for line in f if line.strip() and not line.strip().startswith('#')])
                st.metric("Sample Lines", lines_count)
            except:
                st.metric("Sample Lines", "N/A")
    
    with col3:
        processing_results = st.session_state.get('processing_results', [])
        st.metric("Processed Lines", len(processing_results))
    
    with col4:
        live_feed = st.session_state.get('live_processing_feed', [])
        st.metric("Live Threats", len(live_feed))
    
    # File content preview
    st.subheader("📄 Data Preview")
    
    if data_source == "📤 Upload Custom File" and custom_data_content:
        st.write("**Uploaded File Content (First 10 lines):**")
        lines = custom_data_content.splitlines()
        preview_lines = [line for line in lines[:10] if line.strip()]
        
        for i, line in enumerate(preview_lines, 1):
            st.text(f"{i:2d}: {line}")
            
        if len(lines) > 10:
            st.info(f"... and {len(lines) - 10} more lines")
            
    elif data_source == "📄 Use Sample Traffic Data":
        st.write("**Sample Traffic Data (First 10 lines):**")
        try:
            with open("data/sample_traffic.txt", 'r') as f:
                lines = [line.strip() for line in f if line.strip() and not line.strip().startswith('#')]
                
            for i, line in enumerate(lines[:10], 1):
                st.text(f"{i:2d}: {line}")
                
            if len(lines) > 10:
                st.info(f"... and {len(lines) - 10} more lines")
        except:
            st.error("❌ Could not read sample traffic file")
    
    # Live Processing Status
    if 'live_processing_feed' in st.session_state and st.session_state.live_processing_feed:
        st.subheader("⚡ Live Threat Detection Feed")
        
        # Real-time feed container
        live_container = st.container()
        
        with live_container:
            # Show last 5 detections
            recent_detections = st.session_state.live_processing_feed[-5:]
            recent_detections.reverse()  # Newest first
            
            for detection in recent_detections:
                severity_class = f"alert-{detection['severity'].lower()}"
                st.markdown(f"""
                <div class="{severity_class}" style="margin: 0.3rem 0; padding: 0.8rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <strong>[{detection['timestamp']}] Line {detection['line']}</strong>
                        <span style="font-weight: bold; color: inherit;">{detection['severity']}</span>
                    </div>
                    <div style="margin: 0.5rem 0; font-size: 0.95em;">
                        {detection['message']}
                    </div>
                    <div style="font-size: 0.85em; opacity: 0.9;">
                        🔍 {detection['alert_type'].upper()} Detection | {detection['patterns']}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            # Auto-refresh for live updates
            if st.button("🔄 Refresh Live Feed", key="data_processing_refresh"):
                st.rerun()
    
    # Processing results
    if processing_results:
        st.subheader("🔍 Complete Processing Results")
        
        # Summary statistics
        threats_detected = sum(1 for r in processing_results if r['threat_detected'])
        severity_counts = {}
        pattern_counts = {}
        alert_type_counts = {}
        
        for result in processing_results:
            # Count severities
            sev = result['severity']
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
            
            # Count alert types
            alert_type = result.get('alert_type', 'unknown')
            alert_type_counts[alert_type] = alert_type_counts.get(alert_type, 0) + 1
            
            # Count patterns
            for pattern in result['dfa_detections']:
                pattern_counts[pattern] = pattern_counts.get(pattern, 0) + 1
        
        # Display summary
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Processed", len(processing_results))
        
        with col2:
            st.metric("Threats Found", threats_detected)
        
        with col3:
            threat_rate = (threats_detected / len(processing_results)) * 100 if processing_results else 0
            st.metric("Threat Rate", f"{threat_rate:.1f}%")
        
        with col4:
            critical_high = severity_counts.get('CRITICAL', 0) + severity_counts.get('HIGH', 0)
            st.metric("Critical/High", critical_high)
        
        with col5:
            combined_alerts = alert_type_counts.get('combined', 0)
            st.metric("DFA + AI", combined_alerts)
        
        # Charts section
        col1, col2 = st.columns(2)
        
        with col1:
            # Severity distribution chart
            if severity_counts:
                st.subheader("📊 Severity Distribution")
                fig = px.bar(
                    x=list(severity_counts.keys()),
                    y=list(severity_counts.values()),
                    title="Threats by Severity Level",
                    color=list(severity_counts.keys()),
                    color_discrete_map={
                        'CRITICAL': '#dc2626',
                        'HIGH': '#f59e0b', 
                        'MEDIUM': '#eab308',
                        'LOW': '#10b981'
                    }
                )
                fig.update_layout(showlegend=False, height=400)
                st.plotly_chart(fig, width="stretch")
        
        with col2:
            # Alert type distribution chart
            if alert_type_counts:
                st.subheader("🔍 Detection Type Distribution")
                # Create more descriptive labels
                type_labels = {
                    'dfa': 'DFA Only',
                    'ai': 'AI Only', 
                    'combined': 'DFA + AI',
                    'normal': 'Normal Traffic'
                }
                
                display_labels = [type_labels.get(t, t.title()) for t in alert_type_counts.keys()]
                
                fig = px.pie(
                    values=list(alert_type_counts.values()),
                    names=display_labels,
                    title="Detection Methods Used",
                    color_discrete_map={
                        'DFA Only': '#3b82f6',
                        'AI Only': '#8b5cf6',
                        'DFA + AI': '#dc2626',
                        'Normal Traffic': '#10b981'
                    }
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, width="stretch")
        
        # Pattern analysis
        if pattern_counts:
            st.subheader("🎯 Detected Patterns")
            fig = px.bar(
                x=list(pattern_counts.values()),
                y=list(pattern_counts.keys()),
                orientation='h',
                title="Most Common Attack Patterns"
            )
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed results table
        st.subheader("📋 Detailed Results")
        
        # Filter options
        show_threats_only = st.checkbox("Show Threats Only", value=True)
        
        # Prepare data for display
        filtered_results = processing_results
        if show_threats_only:
            filtered_results = [r for r in processing_results if r['threat_detected']]
        
        if filtered_results:
            # Convert to DataFrame
            df_data = []
            for result in filtered_results:
                # Create alert type display
                alert_type_display = result.get('alert_type', 'unknown').upper()
                if alert_type_display == 'COMBINED':
                    alert_type_display = '🔴 DFA + AI'
                elif alert_type_display == 'DFA':
                    alert_type_display = '🔵 DFA Only'
                elif alert_type_display == 'AI':
                    alert_type_display = '🟣 AI Only'
                elif alert_type_display == 'NORMAL':
                    alert_type_display = '🟢 Normal'
                
                df_data.append({
                    'Line': result['line_number'],
                    'Message': result['message'][:60] + '...' if len(result['message']) > 60 else result['message'],
                    'Detection': alert_type_display,
                    'Severity': result['severity'],
                    'DFA Patterns': ', '.join(result['dfa_detections']) if result['dfa_detections'] else '-',
                    'AI Anomaly': '✓' if result['ai_anomaly'] else '✗',
                    'Time': result['timestamp'].split('T')[1][:8]  # Show only time
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True)
            
            # Export results
            if st.button("📥 Export Results as CSV"):
                csv_data = df.to_csv(index=False)
                st.download_button(
                    label="💾 Download CSV",
                    data=csv_data,
                    file_name=f"ids_processing_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        else:
            st.info("No results to display with current filters.")
    
    else:
        st.info("👆 Select a data source and process data to see results here.")
        
        # Instructions
        st.subheader("📖 Instructions")
        
        st.write("""
        **How to use Data Processing:**
        
        1. **Choose Data Source** (in sidebar):
           - 📄 **Use Sample Traffic Data**: Process the default sample_traffic.txt file
           - 📤 **Upload Custom File**: Upload your own .txt, .log, or .csv file
           - 🔄 **Real-time API Data**: Use live data from the API
        
        2. **Process Data**:
           - Click the appropriate "Process" button in the sidebar
           - **All lines are processed** (no limits!)
           - Progress bar shown for files with 100+ lines
           - Wait for processing to complete
           - View results in this page
        
        3. **Detection Types Explained**:
           - 🔵 **DFA Only**: Pattern-based detection (attack signatures)
           - 🟣 **AI Only**: Anomaly-based detection (unusual behavior)
           - 🔴 **DFA + AI**: Both methods detected threats (highest confidence)
           - 🟢 **Normal**: No threats detected by either method
        
        4. **Analyze Results**:
           - Review threat statistics and detection type charts
           - Export results as CSV for further analysis
           - Use filters to focus on specific types of threats
        """)

elif page == "� 3D Network Topology":
    st.subheader("🌐 3D Network Topology & Attack Visualization")
    
    # Import required libraries
    import networkx as nx
    import numpy as np
    import random
    import math
    
    # Initialize session state for 3D network
    if 'network_attack_active' not in st.session_state:
        st.session_state.network_attack_active = False
    if 'attack_progress' not in st.session_state:
        st.session_state.attack_progress = 0
    if 'compromised_nodes' not in st.session_state:
        st.session_state.compromised_nodes = set()
    
    # Control panel
    st.subheader("🎮 Network Attack Simulation Controls")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        attack_type = st.selectbox("Attack Type", 
                                 ["💥 DDoS Botnet", "🐛 Worm Propagation", "🎯 APT Lateral Movement", "🕷️ Web Crawler Attack"])
    
    with col2:
        network_size = st.slider("Network Size", 10, 50, 25)
    
    with col3:
        attack_speed = st.slider("Attack Speed", 0.5, 5.0, 2.0, 0.5)
    
    with col4:
        if st.button("🚀 Start Attack" if not st.session_state.network_attack_active else "⏹️ Stop Attack"):
            st.session_state.network_attack_active = not st.session_state.network_attack_active
            if st.session_state.network_attack_active:
                st.session_state.attack_progress = 0
                st.session_state.compromised_nodes = set()
    
    # Generate network topology
    def create_network_topology(size):
        G = nx.barabasi_albert_graph(size, 3)  # Scale-free network
        
        # Assign node types
        node_types = {}
        colors = {}
        sizes = {}
        
        for i in range(len(G.nodes())):
            if i == 0:  # Main server
                node_types[i] = "🖥️ Server"
                colors[i] = "#dc2626"  # Red
                sizes[i] = 20
            elif i < 5:  # Critical infrastructure
                node_types[i] = "💻 Critical"
                colors[i] = "#f59e0b"  # Orange
                sizes[i] = 15
            else:  # Regular nodes
                node_types[i] = "🔌 Client"
                colors[i] = "#10b981"  # Green
                sizes[i] = 10
        
        return G, node_types, colors, sizes
    
    # Create 3D positions for nodes
    def get_3d_positions(G):
        # Use spring layout as base
        pos_2d = nx.spring_layout(G, k=3, iterations=50)
        
        # Convert to 3D by adding z-coordinates
        pos_3d = {}
        for node, (x, y) in pos_2d.items():
            # Add some randomness to z-coordinate based on node connectivity
            z = len(list(G.neighbors(node))) * 0.3 + random.uniform(-0.5, 0.5)
            pos_3d[node] = (x * 10, y * 10, z)
        
        return pos_3d
    
    # Generate the network
    G, node_types, colors, sizes = create_network_topology(network_size)
    pos_3d = get_3d_positions(G)
    
    # Simulate attack progression
    if st.session_state.network_attack_active:
        # Update attack progress
        st.session_state.attack_progress += attack_speed * 0.1
        
        # Determine compromised nodes based on attack type
        if attack_type == "💥 DDoS Botnet":
            # DDoS: Random nodes become bots
            if st.session_state.attack_progress > len(st.session_state.compromised_nodes):
                available_nodes = set(G.nodes()) - st.session_state.compromised_nodes
                if available_nodes:
                    new_bot = random.choice(list(available_nodes))
                    st.session_state.compromised_nodes.add(new_bot)
        
        elif attack_type == "🐛 Worm Propagation":
            # Worm: Spreads through connections
            if not st.session_state.compromised_nodes:
                st.session_state.compromised_nodes.add(0)  # Start with server
            else:
                # Spread to neighbors
                for compromised in list(st.session_state.compromised_nodes):
                    neighbors = list(G.neighbors(compromised))
                    uncompromised_neighbors = [n for n in neighbors if n not in st.session_state.compromised_nodes]
                    if uncompromised_neighbors and random.random() < 0.3:
                        st.session_state.compromised_nodes.add(random.choice(uncompromised_neighbors))
        
        elif attack_type == "🎯 APT Lateral Movement":
            # APT: Strategic movement through high-value targets
            if not st.session_state.compromised_nodes:
                st.session_state.compromised_nodes.add(random.randint(5, network_size-1))  # Start with client
            else:
                # Move towards servers and critical infrastructure
                high_value_targets = [i for i in range(5) if i not in st.session_state.compromised_nodes]
                if high_value_targets and random.random() < 0.2:
                    st.session_state.compromised_nodes.add(random.choice(high_value_targets))
        
        elif attack_type == "🕷️ Web Crawler Attack":
            # Web crawler: Systematic scanning
            progress_node = int(st.session_state.attack_progress) % network_size
            if progress_node not in st.session_state.compromised_nodes:
                st.session_state.compromised_nodes.add(progress_node)
    
    # Update colors based on compromise status
    for node in G.nodes():
        if node in st.session_state.compromised_nodes:
            colors[node] = "#991b1b"  # Dark red for compromised
            sizes[node] = sizes[node] * 1.5  # Make compromised nodes larger
    
    # Create 3D network visualization
    edge_x = []
    edge_y = []
    edge_z = []
    
    for edge in G.edges():
        x0, y0, z0 = pos_3d[edge[0]]
        x1, y1, z1 = pos_3d[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])
        edge_z.extend([z0, z1, None])
    
    # Create edge trace
    edge_trace = go.Scatter3d(
        x=edge_x, y=edge_y, z=edge_z,
        mode='lines',
        line=dict(color='rgba(125,125,125,0.5)', width=2),
        hoverinfo='none',
        showlegend=False
    )
    
    # Create node trace
    node_x = [pos_3d[node][0] for node in G.nodes()]
    node_y = [pos_3d[node][1] for node in G.nodes()]
    node_z = [pos_3d[node][2] for node in G.nodes()]
    
    node_colors = [colors[node] for node in G.nodes()]
    node_sizes = [sizes[node] for node in G.nodes()]
    node_text = [f"Node {node}<br>{node_types[node]}<br>{'🚨 COMPROMISED' if node in st.session_state.compromised_nodes else '✅ SECURE'}" 
                 for node in G.nodes()]
    
    node_trace = go.Scatter3d(
        x=node_x, y=node_y, z=node_z,
        mode='markers',
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color='white'),
            opacity=0.8
        ),
        text=node_text,
        hoverinfo='text',
        showlegend=False
    )
    
    # Create attack path traces if attack is active
    attack_traces = []
    if st.session_state.network_attack_active and len(st.session_state.compromised_nodes) > 1:
        # Create pulsing attack paths
        compromised_list = list(st.session_state.compromised_nodes)
        for i in range(len(compromised_list)-1):
            node1, node2 = compromised_list[i], compromised_list[i+1]
            if G.has_edge(node1, node2):  # Only if there's an actual connection
                x0, y0, z0 = pos_3d[node1]
                x1, y1, z1 = pos_3d[node2]
                
                attack_trace = go.Scatter3d(
                    x=[x0, x1], y=[y0, y1], z=[z0, z1],
                    mode='lines',
                    line=dict(color='red', width=8),
                    opacity=0.7,
                    hoverinfo='none',
                    showlegend=False
                )
                attack_traces.append(attack_trace)
    
    # Combine all traces
    data = [edge_trace, node_trace] + attack_traces
    
    # Create the 3D plot
    fig = go.Figure(data=data)
    
    fig.update_layout(
        title=f"3D Network Topology - {attack_type} Attack Simulation",
        scene=dict(
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            zaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            bgcolor='rgba(0,0,0,0)',
            camera=dict(
                up=dict(x=0, y=0, z=1),
                center=dict(x=0, y=0, z=0),
                eye=dict(x=1.5, y=1.5, z=1.5)
            )
        ),
        margin=dict(l=0, r=0, b=0, t=50),
        height=600,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Attack statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Nodes", network_size, "")
    
    with col2:
        compromised_count = len(st.session_state.compromised_nodes)
        st.metric("Compromised Nodes", compromised_count, f"{compromised_count - len(st.session_state.compromised_nodes) if 'prev_compromised' in st.session_state else compromised_count}")
    
    with col3:
        compromise_percentage = (len(st.session_state.compromised_nodes) / network_size) * 100
        st.metric("Network Compromise", f"{compromise_percentage:.1f}%", "")
    
    with col4:
        secure_nodes = network_size - len(st.session_state.compromised_nodes)
        st.metric("Secure Nodes", secure_nodes, "")
    
    # Attack timeline
    if st.session_state.compromised_nodes:
        st.subheader("🕐 Attack Timeline & Analysis")
        
        timeline_data = []
        for i, node in enumerate(st.session_state.compromised_nodes):
            timeline_data.append({
                "Time": f"T+{i*2}s",
                "Event": f"Node {node} compromised",
                "Type": node_types.get(node, "Unknown"),
                "Risk Level": "HIGH" if node < 5 else "MEDIUM"
            })
        
        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            st.dataframe(df_timeline, use_container_width=True)
    
    # Legend and instructions
    st.subheader("📋 Network Legend")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **Node Types:**
        - 🖥️ **Server** (Red): Critical infrastructure
        - 💻 **Critical** (Orange): Important systems  
        - 🔌 **Client** (Green): Regular endpoints
        - 🚨 **Compromised** (Dark Red): Infected nodes
        """)
    
    with col2:
        st.markdown("""
        **Attack Types:**
        - 💥 **DDoS Botnet**: Random node recruitment
        - 🐛 **Worm Propagation**: Network-based spreading
        - 🎯 **APT Lateral Movement**: Strategic infiltration
        - 🕷️ **Web Crawler**: Systematic scanning
        """)
    
    # Auto-refresh for live attack simulation
    if st.session_state.network_attack_active:
        time.sleep(1)
        st.rerun()

elif page == "�🌍 Threat Intelligence":
    st.subheader("🌍 Global Threat Intelligence Center")
    
    # Threat Intelligence Overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🌏 Global Threats", "1,247", "+23 today")
    
    with col2:
        st.metric("🔥 Active Campaigns", "8", "+2 new")
    
    with col3:
        st.metric("🎯 IOCs Tracked", "15,632", "+89 today")
    
    with col4:
        st.metric("⚠️ Risk Level", "HIGH", "↑ Elevated")
    
    # Interactive Threat Map
    st.subheader("🗺️ Global Threat Activity Map")
    
    # Simulated global threat data
    threat_locations = [
        {"country": "Russia", "threats": 342, "lat": 61.5240, "lon": 105.3188, "severity": "high"},
        {"country": "China", "threats": 298, "lat": 35.8617, "lon": 104.1954, "severity": "high"},
        {"country": "USA", "threats": 156, "lat": 37.0902, "lon": -95.7129, "severity": "medium"},
        {"country": "Brazil", "threats": 89, "lat": -14.2350, "lon": -51.9253, "severity": "medium"},
        {"country": "India", "threats": 127, "lat": 20.5937, "lon": 78.9629, "severity": "medium"},
        {"country": "Germany", "threats": 67, "lat": 51.1657, "lon": 10.4515, "severity": "low"},
    ]
    
    # Create map visualization
    import pandas as pd
    df_threats = pd.DataFrame(threat_locations)
    
    # Color mapping
    def get_color(severity):
        colors = {"high": "#dc2626", "medium": "#f59e0b", "low": "#10b981"}
        return colors.get(severity, "#6b7280")
    
    fig = go.Figure(data=go.Scattergeo(
        lon=df_threats['lon'],
        lat=df_threats['lat'],
        text=df_threats['country'] + '<br>Threats: ' + df_threats['threats'].astype(str),
        mode='markers',
        marker=dict(
            size=df_threats['threats'] / 10,
            color=[get_color(s) for s in df_threats['severity']],
            line=dict(width=0.5, color="white"),
            sizemode='diameter'
        )
    ))
    
    fig.update_layout(
        title="Real-time Global Threat Activity",
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
        ),
        height=400
    )
    
    st.plotly_chart(fig, width="stretch")
    
    # Threat Intelligence Feed
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📡 Live Threat Feed")
        
        threat_feed = [
            {"time": "14:32", "threat": "New malware family 'DarkCrypt' detected", "severity": "HIGH"},
            {"time": "14:28", "threat": "APT29 infrastructure changes observed", "severity": "MEDIUM"},
            {"time": "14:25", "threat": "Increased phishing activity targeting banks", "severity": "HIGH"},
            {"time": "14:20", "threat": "Botnet C2 server taken down by authorities", "severity": "LOW"},
            {"time": "14:15", "threat": "Zero-day exploit in popular CMS discovered", "severity": "CRITICAL"}
        ]
        
        for feed_item in threat_feed:
            severity_color = get_severity_color(feed_item["severity"])
            st.markdown(f"""
            <div style="border-left: 4px solid {severity_color}; padding: 0.8rem; margin: 0.5rem 0; background: #f8fafc;">
                <div style="font-weight: bold; color: {severity_color};">[{feed_item['time']}] {feed_item['severity']}</div>
                <div style="margin-top: 0.3rem;">{feed_item['threat']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🎯 Indicators of Compromise (IOCs)")
        
        iocs = [
            {"type": "IP", "value": "192.168.100.5", "description": "C2 Server", "confidence": 95},
            {"type": "Hash", "value": "d4f6c9e2a1b8...", "description": "Malware Sample", "confidence": 98},
            {"type": "Domain", "value": "evil-site.com", "description": "Phishing Domain", "confidence": 92},
            {"type": "URL", "value": "http://badactor.net/...", "description": "Exploit Kit", "confidence": 89}
        ]
        
        for ioc in iocs:
            confidence_color = "#dc2626" if ioc["confidence"] > 90 else "#f59e0b" if ioc["confidence"] > 80 else "#10b981"
            st.markdown(f"""
            <div style="border: 1px solid #e5e7eb; padding: 0.8rem; margin: 0.5rem 0; border-radius: 6px;">
                <div style="display: flex; justify-content: between;">
                    <strong>{ioc['type']}</strong>
                    <span style="color: {confidence_color}; font-weight: bold;">{ioc['confidence']}%</span>
                </div>
                <div style="font-family: monospace; background: #f3f4f6; padding: 0.3rem; margin: 0.3rem 0; border-radius: 3px;">
                    {ioc['value']}
                </div>
                <div style="font-size: 0.9em; color: #6b7280;">{ioc['description']}</div>
            </div>
            """, unsafe_allow_html=True)

elif page == "🎯 Attack Simulator":
    st.subheader("🎯 Advanced Attack Simulation Lab")
    
    st.info("⚠️ **Training Environment Only** - All attacks are simulated and safe")
    
    # Attack Scenario Selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🎮 Choose Your Attack Scenario")
        
        scenarios = {
            "DDoS Attack": {
                "description": "Distributed Denial of Service attack simulation",
                "difficulty": "Beginner",
                "duration": "2 minutes",
                "targets": ["Web Server", "Database", "API Gateway"]
            },
            "Advanced Persistent Threat (APT)": {
                "description": "Multi-stage sophisticated attack campaign",
                "difficulty": "Expert",
                "duration": "15 minutes", 
                "targets": ["Domain Controller", "File Server", "Workstations"]
            },
            "Phishing Campaign": {
                "description": "Social engineering and credential harvesting",
                "difficulty": "Intermediate",
                "duration": "5 minutes",
                "targets": ["Email Server", "Users", "Credentials Database"]
            },
            "Ransomware Outbreak": {
                "description": "File encryption and system compromise",
                "difficulty": "Advanced",
                "duration": "8 minutes",
                "targets": ["File Systems", "Backup Servers", "Network Shares"]
            }
        }
        
        selected_scenario = st.selectbox("Select Attack Scenario", list(scenarios.keys()))
        scenario_info = scenarios[selected_scenario]
        
        # Scenario Details
        st.markdown(f"""
        **📋 Scenario Details:**
        - **Description:** {scenario_info['description']}
        - **Difficulty:** {scenario_info['difficulty']}
        - **Estimated Duration:** {scenario_info['duration']}
        - **Primary Targets:** {', '.join(scenario_info['targets'])}
        """)
    
    with col2:
        st.subheader("🏆 Simulation Stats")
        st.metric("Scenarios Completed", "12", "+3 this week")
        st.metric("Average Response Time", "3.2 min", "-0.8 min")
        st.metric("Detection Rate", "94.2%", "+2.1%")
        
        # Achievement badges
        st.subheader("🎖️ Achievements")
        badges = ["🔰 First Detection", "🎯 Perfect Score", "⚡ Speed Demon", "🛡️ Defender"]
        for badge in badges:
            st.markdown(f"- {badge}")
    
    # Attack Configuration
    st.subheader("⚙️ Attack Parameters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        intensity = st.slider("Attack Intensity", 1, 10, 5)
        st.caption("Higher intensity = More aggressive attack patterns")
    
    with col2:
        stealth = st.slider("Stealth Level", 1, 10, 3)
        st.caption("Higher stealth = Harder to detect")
    
    with col3:
        duration = st.slider("Duration (minutes)", 1, 30, 5)
        st.caption("How long the attack simulation runs")
    
    # Launch Attack
    if st.button("🚀 Launch Attack Simulation", type="primary"):
        st.success("🎯 Attack simulation launched!")
        
        # Progress bar
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Simulated attack phases
        phases = [
            "🔍 Reconnaissance phase initiated",
            "🚪 Initial access attempt",
            "🔑 Privilege escalation in progress", 
            "📡 Command & Control established",
            "💾 Data exfiltration detected",
            "🔒 Attack objectives completed"
        ]
        
        for i, phase in enumerate(phases):
            time.sleep(0.5)  # Simulate time delay
            progress_bar.progress((i + 1) / len(phases))
            status_text.text(f"Phase {i+1}/6: {phase}")
        
        st.balloons()  # Celebration effect
        st.success("✅ Simulation completed! Check the results below.")
        
        # Results summary
        st.subheader("📊 Simulation Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Detection Time", "2.3 min", "-0.5 min")
        with col2:
            st.metric("Alerts Triggered", "8", "+2")
        with col3:
            st.metric("False Positives", "1", "-1")
        with col4:
            st.metric("Response Score", "92/100", "+5 pts")

elif page == "🤖 AI Insights":
    st.subheader("🤖 AI-Powered Security Insights")
    
    # AI Summary Section
    st.subheader("📝 AI Threat Summary")
    
    ai_summary = """
    🤖 **AI Analysis for the last 24 hours:**
    
    Based on my analysis of your network traffic and threat patterns, I've identified several key insights:
    
    **🔍 Pattern Recognition:**
    - Detected a 34% increase in scan attempts during off-hours (2-6 AM)
    - Identified 3 new attack signatures not in your current DFA patterns
    - Found correlations between failed login attempts and subsequent malware downloads
    
    **⚠️ Risk Assessment:**
    - **HIGH RISK**: Unusual outbound connections to recently registered domains
    - **MEDIUM RISK**: Increased phishing attempts targeting your email domain
    - **LOW RISK**: Normal fluctuations in network traffic patterns
    
    **💡 Recommendations:**
    1. Implement additional monitoring for off-hours activities
    2. Update DFA patterns to include newly discovered attack signatures
    3. Enhance email filtering rules for domain-specific phishing protection
    4. Consider implementing behavioral analysis for outbound connections
    """
    
    st.markdown(ai_summary)
    
    # Predictive Analytics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔮 Threat Predictions")
        
        predictions = [
            {"threat": "Phishing Campaign", "probability": 78, "timeframe": "Next 48 hours"},
            {"threat": "Brute Force Attack", "probability": 45, "timeframe": "Next week"},
            {"threat": "Malware Outbreak", "probability": 23, "timeframe": "Next month"},
            {"threat": "DDoS Attempt", "probability": 67, "timeframe": "Weekend"}
        ]
        
        for pred in predictions:
            prob_color = "#dc2626" if pred["probability"] > 70 else "#f59e0b" if pred["probability"] > 40 else "#10b981"
            
            st.markdown(f"""
            <div style="border: 1px solid #e5e7eb; padding: 1rem; margin: 0.5rem 0; border-radius: 8px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <strong>{pred['threat']}</strong>
                    <span style="color: {prob_color}; font-weight: bold;">{pred['probability']}%</span>
                </div>
                <div style="background: #f3f4f6; height: 8px; border-radius: 4px;">
                    <div style="background: {prob_color}; height: 8px; width: {pred['probability']}%; border-radius: 4px;"></div>
                </div>
                <div style="font-size: 0.9em; color: #6b7280; margin-top: 0.3rem;">Expected: {pred['timeframe']}</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🧠 Behavioral Analysis")
        
        # Simulated behavioral insights
        behaviors = {
            "Normal Business Hours": 85,
            "After Hours Activity": 15,
            "Weekend Traffic": 8,
            "External Connections": 23,
            "Admin Access": 12,
            "File Transfers": 34
        }
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(behaviors.keys()),
                y=list(behaviors.values()),
                marker_color=['#10b981' if v < 30 else '#f59e0b' if v < 60 else '#dc2626' for v in behaviors.values()]
            )
        ])
        
        fig.update_layout(
            title="Network Behavior Baseline vs Current",
            xaxis_title="Activity Type",
            yaxis_title="Activity Level (%)",
            height=300
        )
        
        st.plotly_chart(fig, width="stretch")
    
    # AI Chat Assistant
    st.subheader("💬 AI Security Assistant")
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [
            {"role": "assistant", "content": "Hello! I'm your AI security assistant. I can help analyze threats, explain attack patterns, and provide security recommendations. What would you like to know?"}
        ]
    
    # Display chat history
    for message in st.session_state.chat_history[-5:]:  # Show last 5 messages
        if message["role"] == "assistant":
            st.markdown(f"🤖 **AI Assistant:** {message['content']}")
        else:
            st.markdown(f"👤 **You:** {message['content']}")
    
    # Chat input
    user_input = st.text_input("Ask the AI assistant:", placeholder="e.g., 'Explain this attack pattern' or 'How can I improve my security posture?'")
    
    if st.button("Send") and user_input:
        # Add user message
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Generate AI response (simplified - in real app, use actual AI/LLM)
        ai_responses = {
            "attack": "Based on the patterns I'm seeing, this appears to be a multi-stage attack. The initial reconnaissance phase was followed by credential harvesting, and now we're seeing lateral movement attempts.",
            "improve": "I recommend implementing these security improvements: 1) Enable multi-factor authentication, 2) Update your intrusion detection rules, 3) Implement network segmentation, 4) Regular security awareness training.",
            "threat": "This threat pattern matches known APT group behaviors. I suggest increasing monitoring levels and implementing additional endpoint protection measures.",
            "default": "I understand you're asking about security. Based on current threat intelligence, I recommend focusing on email security, network monitoring, and user education as key priorities."
        }
        
        # Simple keyword matching for demo
        response = ai_responses.get("default", ai_responses["default"])
        for keyword in ai_responses:
            if keyword in user_input.lower():
                response = ai_responses[keyword]
                break
        
        st.session_state.chat_history.append({"role": "assistant", "content": response})
        st.rerun()

elif page == "⚙️ Settings & Configuration":
    st.subheader("⚙️ System Settings & Configuration")
    
    # Detection Engine Settings
    st.subheader("🔧 Detection Engine Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**DFA Engine Settings:**")
        dfa_enabled = st.checkbox("Enable DFA Detection", value=True)
        dfa_sensitivity = st.slider("DFA Sensitivity", 1, 10, 7)
        dfa_patterns = st.number_input("Active Patterns", min_value=1, max_value=100, value=25)
        
        st.markdown("**AI Engine Settings:**")
        ai_enabled = st.checkbox("Enable AI Detection", value=True)
        ai_threshold = st.slider("Anomaly Threshold", 0.1, 1.0, 0.7, 0.1)
        ai_model_version = st.selectbox("Model Version", ["v2.1", "v2.0", "v1.9"])
    
    with col2:
        st.markdown("**Alert Settings:**")
        alert_sound = st.checkbox("Enable Alert Sounds", value=True)
        email_notifications = st.checkbox("Email Notifications", value=False)
        sms_notifications = st.checkbox("SMS Notifications", value=False)
        
        st.markdown("**Performance Settings:**")
        refresh_rate = st.slider("Dashboard Refresh Rate (seconds)", 1, 60, 5)
        max_alerts = st.number_input("Max Alerts to Display", min_value=10, max_value=1000, value=100)
        log_retention = st.selectbox("Log Retention Period", ["7 days", "30 days", "90 days", "1 year"])
    
    # Network Configuration
    st.subheader("🌐 Network Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Monitoring Settings:**")
        monitor_internal = st.checkbox("Monitor Internal Traffic", value=True)
        monitor_external = st.checkbox("Monitor External Traffic", value=True)
        
        network_interfaces = st.multiselect(
            "Network Interfaces to Monitor",
            ["eth0", "eth1", "wlan0", "lo"],
            default=["eth0", "wlan0"]
        )
    
    with col2:
        st.markdown("**Whitelist Configuration:**")
        trusted_ips = st.text_area(
            "Trusted IP Addresses (one per line)",
            value="192.168.1.1\n10.0.0.1\n127.0.0.1"
        )
        
        trusted_domains = st.text_area(
            "Trusted Domains (one per line)", 
            value="company.com\ngoogle.com\nmicrosoft.com"
        )
    
    # Export/Import Configuration
    st.subheader("📁 Configuration Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Export Configuration"):
            config_data = {
                "dfa_enabled": dfa_enabled,
                "dfa_sensitivity": dfa_sensitivity,
                "ai_enabled": ai_enabled,
                "ai_threshold": ai_threshold,
                "refresh_rate": refresh_rate,
                "max_alerts": max_alerts
            }
            
            st.download_button(
                label="Download Config File",
                data=str(config_data),
                file_name="ids_config.json",
                mime="application/json"
            )
    
    with col2:
        uploaded_config = st.file_uploader("📂 Import Configuration", type="json")
        if uploaded_config is not None:
            st.success("Configuration imported successfully!")
    
    with col3:
        if st.button("🔄 Reset to Defaults"):
            st.warning("Configuration reset to default values!")
    
    # System Status
    st.subheader("📊 System Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("System Uptime", "2d 14h 23m", "")
    
    with col2:
        st.metric("CPU Usage", "23.4%", "-2.1%")
    
    with col3:
        st.metric("Memory Usage", "1.2GB", "+0.1GB")
    
    with col4:
        st.metric("Disk Usage", "45.2GB", "+2.3GB")
    
    # Save Configuration
    if st.button("💾 Save All Settings", type="primary"):
        st.success("⚡ Configuration saved successfully!")
        st.balloons()
    
    # API Configuration
    st.subheader("🔗 API Configuration")
    api_url = st.text_input("API Base URL", value=st.session_state.get('api_url', "http://localhost:5000"))
    st.session_state.api_url = api_url
    
    if st.button("Test API Connection"):
        try:
            response = requests.get(f"{api_url}/health", timeout=5)
            if response.status_code == 200:
                st.success("✅ API connection successful!")
                st.json(response.json())
            else:
                st.error(f"❌ API connection failed with status code: {response.status_code}")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ API connection failed: {str(e)}")
    
    # Dashboard Settings
    st.subheader("📊 Dashboard Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.number_input("Default Refresh Interval (seconds)", 
                       min_value=1, max_value=300, 
                       value=st.session_state.refresh_interval)
        
        theme_mode = st.selectbox("Theme Mode", ["Professional Blue", "Dark Mode", "Light Mode"])
    
    with col2:
        max_alerts_display = st.number_input("Max Alerts to Display", 
                                           min_value=10, max_value=1000, 
                                           value=100)
        
        enable_sound_alerts = st.checkbox("Enable Sound Alerts", value=False)
    
    # System Information
    st.subheader("🖥️ System Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Application Info:**")
        st.write("• Dashboard Version: 1.0.0")
        st.write("• Streamlit Version:", st.__version__)
        st.write("• Python Version:", os.sys.version.split()[0])
    
    with col2:
        st.write("**File Paths:**")
        st.write("• Current Directory:", Path.cwd())
        st.write("• Models Directory:", Path("models").absolute())
        st.write("• Data Directory:", Path("data").absolute())
    
    # Export/Import Settings
    st.subheader("⚙️ Export/Import Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📥 Export Settings"):
            settings = {
                'api_url': api_url,
                'refresh_interval': st.session_state.refresh_interval,
                'theme_mode': theme_mode,
                'max_alerts_display': max_alerts_display,
                'enable_sound_alerts': enable_sound_alerts,
                'exported_at': datetime.now().isoformat()
            }
            st.download_button(
                label="💾 Download Settings File",
                data=json.dumps(settings, indent=2),
                file_name=f"ids_dashboard_settings_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
    
    with col2:
        uploaded_file = st.file_uploader("📤 Import Settings", type=['json'])
        if uploaded_file is not None:
            try:
                settings = json.load(uploaded_file)
                st.success("✅ Settings imported successfully!")
                st.json(settings)
            except json.JSONDecodeError:
                st.error("❌ Invalid settings file format")

# Auto-refresh functionality with enhanced live updates
if st.session_state.auto_refresh and page == "🏠 Real-time Dashboard":
    # Create a placeholder for countdown
    if 'countdown_placeholder' not in st.session_state:
        st.session_state.countdown_placeholder = st.empty()
    
    # Show countdown in sidebar
    with st.sidebar:
        countdown_container = st.empty()
        for remaining in range(st.session_state.refresh_interval, 0, -1):
            countdown_container.info(f"🔄 Auto-refresh in {remaining}s")
            time.sleep(1)
        countdown_container.empty()
    
    st.rerun()

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #6b7280; margin-top: 2rem;">
    <p>🛡️ IDS Security Dashboard v1.0 | Built with Streamlit | Real-time Network Security Monitoring</p>
</div>
""", unsafe_allow_html=True)