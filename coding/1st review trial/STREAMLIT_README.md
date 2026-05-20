# 🛡️ IDS Security Dashboard - Streamlit Frontend

A professional web-based frontend for the AI-Driven Intrusion Detection System, providing real-time monitoring, alert management, and comprehensive analytics.

## 🌟 Features

### 🏠 Real-time Dashboard
- **Live System Monitoring**: Real-time CPU, memory, and system resource tracking
- **Alert Stream**: Continuous display of security alerts with color-coded severity levels
- **System Status**: Live status of API server and system components
- **Auto-refresh**: Configurable automatic refresh for real-time updates

### 🚨 Alert Management
- **Comprehensive Alert View**: Detailed view of all security alerts
- **Advanced Filtering**: Filter by severity, type, patterns, and time ranges
- **Alert Details**: JSON view of complete alert information
- **Interactive Data Tables**: Sortable and searchable alert displays

### 📈 System Analytics
- **Performance Metrics**: Visual charts of system resource usage
- **Alert Statistics**: Pie charts and bar graphs of alert distributions
- **Pattern Analysis**: Most frequent threat patterns and trends
- **Timeline View**: Historical alert timeline with scatter plots

### ⚙️ Settings & Configuration
- **API Configuration**: Configure API endpoints and test connections
- **Dashboard Settings**: Customize refresh intervals, themes, and display options
- **Export/Import**: Save and load dashboard configurations
- **System Information**: View application and system details

## 🚀 Quick Start

### Prerequisites
- Python 3.13+ installed
- All IDS system components (from the main project)

### 1. Install Dependencies
The startup script will handle this automatically, or manually install:
```bash
pip install streamlit plotly pandas altair watchdog psutil
```

### 2. Start All Services
Use the automated startup script:
```bash
python start_services.py
```

This will start:
- ✅ API Server (port 5000)
- ✅ Streamlit Dashboard (port 8501)

### 3. Manual Startup (Alternative)

Start each component separately:

```bash
# Terminal 1: Start API Server
python api.py

# Terminal 2: Start Streamlit Dashboard
streamlit run streamlit_app.py

# Terminal 3: Generate Test Data (Optional)
python generate_test_data.py

# Terminal 4: Run IDS Processor (Optional)
python main.py --file data/sample_traffic.txt
```

### 4. Access the Dashboard
Open your web browser and navigate to:
- **Dashboard URL**: http://localhost:8501
- **API Server**: http://localhost:5000

## 📱 Using the Dashboard

### Real-time Monitoring
1. Navigate to "🏠 Real-time Dashboard"
2. Enable auto-refresh in the sidebar
3. Monitor live system metrics and alerts
4. View recent alerts with severity indicators

### Managing Alerts  
1. Go to "🚨 Alert Management"
2. Use filters to find specific alerts
3. Click "Show Detailed View" for JSON details
4. Export alert data if needed

### Analytics & Reporting
1. Visit "📈 System Analytics" 
2. View system resource usage graphs
3. Analyze alert patterns and trends
4. Check historical timeline data

### Configuration
1. Access "⚙️ Settings & Configuration"
2. Test API connectivity
3. Adjust refresh intervals
4. Export/import settings

## 🎨 Professional Theme Features

### Visual Design
- **Modern UI**: Clean, professional interface with gradient headers
- **Color-coded Alerts**: Severity-based color scheme (Red=Critical, Yellow=Medium, Green=Low)
- **Responsive Layout**: Adapts to different screen sizes
- **Interactive Charts**: Plotly-powered visualizations

### Real-time Updates
- **Auto-refresh**: Configurable refresh intervals (1-30 seconds)
- **Live Metrics**: Real-time system resource monitoring
- **Stream Processing**: Continuous alert updates without page reload

## 📊 Dashboard Components

### Metrics Cards
```
📊 Total Alerts    🔗 API Status    💻 CPU Usage    💾 Memory Usage
    156               🟢 Online        23.4%           67.2%
```

### Alert Display
```
🚨 CRITICAL - 2025-09-27 14:30:25
Message: DDoS attack ongoing from multiple IPs
Patterns: ddos, attack
Type: dfa
```

### System Gauges
- CPU usage gauge with color-coded thresholds
- Memory usage visualization
- Real-time performance monitoring

## 🧪 Testing with Generated Data

Use the included data generator to create realistic test scenarios:

```bash
python generate_test_data.py
```

This generates:
- **Normal Traffic**: Typical system operations
- **Attack Scenarios**: Simulated security incidents
- **Realistic Timing**: Variable intervals between events
- **Multiple Severities**: All alert levels for testing

## 🔧 Customization

### Theme Modification
Edit the CSS in `streamlit_app.py`:
```python
st.markdown("""
<style>
    .header-container {
        background: linear-gradient(90deg, #your-color-1, #your-color-2);
        /* Your custom styling */
    }
</style>
""", unsafe_allow_html=True)
```

### Adding New Pages
1. Add new page option to sidebar selectbox
2. Create elif condition for your page
3. Add page content and functionality

### Custom Metrics
Add new metrics to the dashboard:
```python
def get_custom_metrics():
    # Your custom metric calculation
    return metric_value

# Display in dashboard
st.metric("Custom Metric", get_custom_metrics())
```

## 📁 File Structure

```
streamlit_app.py              # Main Streamlit application
start_services.py             # Automated startup script
generate_test_data.py         # Test data generator
├── Real-time Dashboard       # Live monitoring page
├── Alert Management          # Alert viewing and filtering
├── System Analytics          # Charts and statistics
└── Settings                  # Configuration options
```

## 🔍 Troubleshooting

### Common Issues

**Dashboard not loading:**
- Check if Streamlit is installed: `pip list | grep streamlit`
- Verify Python version: `python --version`
- Ensure port 8501 is available

**No alerts showing:**
- Verify API server is running: `curl http://localhost:5000/health`
- Check API connectivity in Settings page
- Generate test data: `python generate_test_data.py`

**Performance issues:**
- Reduce auto-refresh interval in sidebar
- Clear cache: Use "Manual Refresh" button
- Check system resources in Analytics page

### Debug Mode
Run Streamlit in debug mode:
```bash
streamlit run streamlit_app.py --server.runOnSave true --logger.level debug
```

## 🎯 Advanced Features

### API Integration
The dashboard integrates with the IDS API for:
- Real-time alert retrieval
- System health monitoring  
- Alert creation and management
- Performance metrics

### Data Visualization
- **Plotly Charts**: Interactive graphs and gauges
- **Pandas Integration**: Data manipulation and filtering
- **Real-time Updates**: Live data streaming
- **Export Capabilities**: Download charts and data

### Security Features
- **Input Validation**: Sanitized user inputs
- **Error Handling**: Graceful degradation on failures
- **Connection Testing**: API health checks
- **Secure Defaults**: Safe configuration options

## 🚀 Production Deployment

### Configuration for Production
1. Update API URLs in settings
2. Set appropriate refresh intervals
3. Configure authentication if needed
4. Enable HTTPS for secure connections

### Performance Optimization
- Use caching for expensive operations
- Implement pagination for large datasets
- Optimize chart rendering
- Monitor memory usage

## 📋 Keyboard Shortcuts

- **Ctrl+R**: Manual refresh
- **Ctrl+Shift+R**: Clear cache and refresh  
- **F11**: Full screen mode
- **Ctrl+**: Zoom in
- **Ctrl+-**: Zoom out

## 🤝 Contributing

To add new features:
1. Follow the existing code structure
2. Add new pages using the sidebar navigation pattern
3. Implement proper error handling
4. Test with the data generator
5. Update this documentation

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Verify all services are running
3. Check browser console for errors
4. Test API connectivity independently

---

**Built with ❤️ using Streamlit | Professional Network Security Monitoring**