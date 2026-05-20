# 📁 File Upload Feature Guide

## Overview
The Streamlit dashboard now includes a flexible data input system that allows you to choose between different data sources for analysis.

## 🎯 Data Source Options

### 1. 📄 Use Sample Traffic Data (Default)
- **What it does**: Uses the built-in `sample_traffic.txt` file
- **Best for**: Quick testing and demonstration
- **Contains**: 
  - Normal network traffic patterns
  - Various attack signatures (DDoS, malware, injection, etc.)
  - Mixed security scenarios
  - ~80+ realistic examples

**How to use:**
1. Select "📄 Use Sample Traffic Data" in the sidebar
2. Click "🔄 Process Sample Data" button
3. View results in the "🗂️ Data Processing" page

### 2. 📤 Upload Custom File (NEW!)
- **What it does**: Allows you to upload your own traffic/log files
- **Best for**: Analyzing your own network data or custom scenarios
- **Supported formats**: .txt, .log, .csv files

**File Format Requirements:**
```
# Comments start with # (optional)
normal user login
attack detected in system
scan attempt from IP 192.168.1.100
unauthorized access blocked
# Each line = one network event
```

**How to use:**
1. Select "📤 Upload Custom File" in the sidebar
2. Click "Choose file" and select your data file
3. Review the file preview and statistics
4. Click "🔄 Process Uploaded Data" button
5. View results in the "🗂️ Data Processing" page

### 3. 🔄 Real-time API Data
- **What it does**: Uses live data from the running API server
- **Best for**: Continuous monitoring and real-time analysis
- **Features**: Auto-refresh, live alerts, system monitoring

## 📋 File Upload Instructions

### Step 1: Prepare Your Data File
Create a text file with one network event per line:

```txt
user login successful
database query executed  
attack pattern detected
scan attempt blocked
file access granted
unauthorized access denied
malware signature found
system backup completed
```

### Step 2: Upload via Dashboard
1. Open the Streamlit dashboard: http://localhost:8501
2. In the sidebar, select "📤 Upload Custom File"
3. Click the file uploader
4. Choose your .txt, .log, or .csv file
5. Review the upload confirmation and file statistics

### Step 3: Process and Analyze
1. Click "🔄 Process Uploaded Data" in the sidebar
2. Navigate to "🗂️ Data Processing" page
3. Review the analysis results:
   - Threat detection statistics
   - Severity level distribution
   - Attack pattern identification
   - Detailed line-by-line results

## 📊 What You'll See After Processing

### Summary Metrics
- **Total Processed**: Number of lines analyzed
- **Threats Found**: Count of detected security issues
- **Threat Rate**: Percentage of lines with threats
- **Critical/High**: Count of serious threats

### Visualizations
- **Severity Distribution**: Bar chart of threat levels
- **Pattern Analysis**: Most common attack types
- **Detailed Results Table**: Line-by-line breakdown

### Export Options
- Download results as CSV file
- Export processing configurations
- Save analysis reports

## 🧪 Testing with Sample Files

### Option 1: Download Built-in Sample
1. Select "📤 Upload Custom File"
2. Click "📥 Download Sample File" in sidebar
3. Save the `sample_custom_data.txt` file
4. Upload it back to test the feature

### Option 2: Create Your Own Test File
```txt
# My Custom Network Events
normal web traffic
user authentication passed
attack vector in payload
sql injection blocked
scan attempt detected
file upload successful
malware quarantined
system alert triggered
```

### Option 3: Use Real Log Files
- Web server logs (Apache, Nginx)
- Firewall logs
- IDS/IPS system outputs
- Network monitoring data
- Security event logs

## 🔍 Analysis Features

### Threat Detection
The system analyzes each line for:
- **DFA Pattern Matching**: Known attack signatures
- **AI Anomaly Detection**: Unusual behavior patterns
- **Severity Assessment**: Risk level classification

### Supported Patterns
- `attack` - General attack indicators
- `unauthorized access` - Access violations
- `scan attempt` - Network scanning
- `malware` - Malicious software
- `injection` - Code injection attacks
- `bruteforce` - Password attacks
- `ddos` - Distributed denial of service
- `phishing` - Social engineering attempts

## 💡 Tips and Best Practices

### File Preparation
- Keep files under 1000 lines for optimal performance
- Use clear, descriptive event descriptions
- Include timestamps if available
- Separate different log types into different files

### Performance Optimization  
- Large files are automatically limited to 50 lines for processing
- Use comments (#) to add context without affecting analysis
- Process files in smaller batches for better responsiveness

### Troubleshooting
**File won't upload:**
- Check file format (.txt, .log, .csv only)
- Ensure file size is reasonable (<10MB)
- Try saving with UTF-8 encoding

**No threats detected:**
- Check if your data contains recognizable attack patterns
- Try the sample file first to verify system works
- Ensure file format matches expectations

**Processing takes too long:**
- Break large files into smaller chunks
- Remove unnecessary comment lines
- Use the sample data for initial testing

## 🚀 Advanced Usage

### Integration with Existing Systems
1. Export logs from your security tools
2. Convert to simple text format (one event per line)
3. Upload and analyze in the dashboard
4. Export results for reporting

### Automated Workflows
1. Set up log export from your systems
2. Use the API endpoints to submit data programmatically
3. Monitor results via the dashboard
4. Set up alerts for critical findings

### Custom Pattern Development
1. Analyze your uploaded data patterns
2. Note frequently missed threats
3. Customize the DFA patterns in `dfa_engine.py`
4. Retrain AI model with your specific data

## 📈 Next Steps

After analyzing your data:
1. **Review Results**: Check threat detection accuracy
2. **Export Reports**: Download CSV for further analysis  
3. **Tune System**: Adjust patterns based on your data
4. **Automate Process**: Set up regular data uploads
5. **Monitor Live**: Switch to real-time API mode for continuous monitoring

---

**The file upload feature makes the IDS system flexible and adaptable to your specific network security needs!** 🛡️