"""
Simple REST API for IDS Alert Management
Provides endpoints to view and manage security alerts
"""

from flask import Flask, jsonify, request
import logging
from datetime import datetime

def setup_logging():
    """Configure logging for the API"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

app = Flask(__name__)
logger = setup_logging()

# In-memory storage for alerts
alerts = []

class Alert:
    def __init__(self, message, alert_type, severity, line_number=None, line_content=None, detected_patterns=None, timestamp=None):
        self.message = message
        self.alert_type = alert_type  # 'dfa', 'ai', or 'combined'
        self.severity = severity      # 'low', 'medium', 'high'
        self.line_number = line_number
        self.line_content = line_content
        self.detected_patterns = detected_patterns or []
        self.timestamp = timestamp or datetime.now().isoformat()
    
    def to_dict(self):
        return {
            'message': self.message,
            'alert_type': self.alert_type,
            'severity': self.severity,
            'line_number': self.line_number,
            'line_content': self.line_content,
            'detected_patterns': self.detected_patterns,
            'timestamp': self.timestamp
        }

@app.route('/alerts', methods=['GET'])
def get_alerts():
    """Get all alerts"""
    try:
        alerts_data = [alert.to_dict() for alert in alerts]
        logger.info(f"Retrieved {len(alerts_data)} alerts")
        return jsonify({
            'status': 'success',
            'count': len(alerts_data),
            'alerts': alerts_data
        })
    except Exception as e:
        logger.error(f"Error retrieving alerts: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/alerts/<int:alert_id>', methods=['GET'])
def get_alert(alert_id):
    """Get a specific alert by ID"""
    try:
        if alert_id < 0 or alert_id >= len(alerts):
            return jsonify({'status': 'error', 'message': 'Alert not found'}), 404
        
        alert = alerts[alert_id]
        logger.info(f"Retrieved alert {alert_id}")
        return jsonify({
            'status': 'success',
            'alert': alert.to_dict()
        })
    except Exception as e:
        logger.error(f"Error retrieving alert {alert_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/alerts', methods=['POST'])
def create_alert():
    """Create a new alert"""
    try:
        data = request.get_json()
        
        if not data or 'message' not in data:
            return jsonify({'status': 'error', 'message': 'Message is required'}), 400
        
        alert_type = data.get('alert_type', 'unknown')
        severity = data.get('severity', 'medium')
        line_number = data.get('line_number')
        line_content = data.get('line_content')
        detected_patterns = data.get('detected_patterns', [])
        
        alert = Alert(
            message=data['message'],
            alert_type=alert_type,
            severity=severity,
            line_number=line_number,
            line_content=line_content,
            detected_patterns=detected_patterns
        )
        
        alerts.append(alert)
        logger.info(f"Created new alert: {data['message']} (Line {line_number})")
        
        return jsonify({
            'status': 'success',
            'message': 'Alert created',
            'alert': alert.to_dict(),
            'alert_id': len(alerts) - 1
        }), 201
        
    except Exception as e:
        logger.error(f"Error creating alert: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/alerts/<int:alert_id>', methods=['DELETE'])
def delete_alert(alert_id):
    """Delete an alert by ID"""
    try:
        if alert_id < 0 or alert_id >= len(alerts):
            return jsonify({'status': 'error', 'message': 'Alert not found'}), 404
        
        deleted_alert = alerts.pop(alert_id)
        logger.info(f"Deleted alert {alert_id}: {deleted_alert.message}")
        
        return jsonify({
            'status': 'success',
            'message': 'Alert deleted',
            'deleted_alert': deleted_alert.to_dict()
        })
    except Exception as e:
        logger.error(f"Error deleting alert {alert_id}: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'alerts_count': len(alerts)
    })

if __name__ == "__main__":
    logger.info("Starting IDS API server on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)
