# IDS API Usage Guide

## Overview
The IDS API provides a RESTful interface for managing security alerts detected by the AI-Driven Intrusion Detection System. It runs on `http://localhost:5000` and supports CRUD operations for alerts.

## API Endpoints

### 1. Health Check
**GET** `/health`
- Checks if the API is running
- Returns system status and alert count

**Example:**
```bash
curl http://localhost:5000/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-08-30T10:05:01.402000",
  "alerts_count": 0
}
```

### 2. Get All Alerts
**GET** `/alerts`
- Retrieves all stored alerts
- Returns alert details with metadata

**Example:**
```bash
curl http://localhost:5000/alerts
```

**Response:**
```json
{
  "status": "success",
  "count": 3,
  "alerts": [
    {
      "message": "attack detected",
      "alert_type": "dfa",
      "severity": "high",
      "line_number": 42,
      "line_content": "attack detected",
      "detected_patterns": ["attack"],
      "timestamp": "2025-08-30T09:59:35.226556"
    }
  ]
}
```

### 3. Get Specific Alert
**GET** `/alerts/{id}`
- Retrieves a specific alert by ID (0-based index)

**Example:**
```bash
curl http://localhost:5000/alerts/0
```

### 4. Create Alert
**POST** `/alerts`
- Creates a new alert
- Requires JSON payload with message

**Example:**
```bash
curl -X POST http://localhost:5000/alerts \
  -H "Content-Type: application/json" \
  -d '{
    "message": "test alert",
    "alert_type": "manual",
    "severity": "medium",
    "line_number": 123,
    "line_content": "test alert content",
    "detected_patterns": ["test_pattern"]
  }'
```

**Required Fields:**
- `message`: The alert message/content

**Optional Fields:**
- `alert_type`: Type of alert (default: "unknown")
- `severity`: Severity level (default: "medium")

### 5. Delete Alert
**DELETE** `/alerts/{id}`
- Deletes a specific alert by ID

**Example:**
```bash
curl -X DELETE http://localhost:5000/alerts/0
```

## Integration with Main IDS System

The main IDS system (`main.py`) automatically sends alerts to this API when threats are detected. The integration includes:

- **Automatic Alert Creation**: When DFA patterns or AI anomalies are detected
- **Error Handling**: Graceful handling of API connection failures
- **Real-time Updates**: Alerts are sent immediately upon detection

## Alert Types and Severity Levels

### Alert Types:
- `dfa`: Pattern-based detection using Deterministic Finite Automata
- `ai`: Anomaly detection using machine learning
- `combined`: Both DFA and AI detection triggered
- `manual`: Manually created alerts

### Enhanced Alert Response Fields:
- `line_number`: The line number where the threat was detected (for file processing)
- `line_content`: The actual content of the line that triggered the alert
- `detected_patterns`: Array of specific DFA pattern names that were matched
  - `attack`: General attack pattern detected
  - `unauthorized access`: Unauthorized access attempt
  - `scan attempt`: Network scanning activity
  - `malware`: Malware-related activity
  - `injection`: Code injection attempt
  - `bruteforce`: Brute force attack
  - `ddos`: DDoS attack pattern
  - `phishing`: Phishing attempt

### Severity Levels:
- `low`: Minor security events (e.g., scan attempts)
- `medium`: Moderate security events (e.g., AI anomalies)
- `high`: Serious security events (e.g., attack patterns)
- `critical`: Critical security events (e.g., malware, DDoS)

## Usage Examples

### 1. Monitor System Health
```bash
# Check if API is running
curl http://localhost:5000/health
```

### 2. View All Alerts
```bash
# Get all stored alerts
curl http://localhost:5000/alerts | python -m json.tool
```

### 3. Create Manual Alert
```bash
# Manually create an alert
curl -X POST http://localhost:5000/alerts \
  -H "Content-Type: application/json" \
  -d '{"message": "Manual security check", "severity": "medium"}'
```

### 4. Delete Specific Alert
```bash
# Delete alert with ID 5
curl -X DELETE http://localhost:5000/alerts/5
```

### 5. Integration Testing
```bash
# Test API connectivity
python test_api_integration.py
```

## Error Handling

The API includes comprehensive error handling:
- Invalid requests return appropriate HTTP status codes
- Connection errors are logged but don't stop the main IDS processing
- Missing parameters return descriptive error messages

## Storage

- **In-memory storage**: Alerts are stored in memory (lost on server restart)
- **Future enhancement**: Could be extended to use database persistence

## Running the API

Start the API server:
```bash
python api.py
```

The API will be available at: `http://localhost:5000`
