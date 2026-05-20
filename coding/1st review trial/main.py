

import argparse
import logging
import time
import datetime
import requests
from pathlib import Path
from dfa_engine import check_all_patterns
from ai_module import AIDetector

# ANSI color codes for terminal output
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def setup_logging():
    """Configure enhanced logging for the orchestrator"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

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

def format_threat_message(severity, message):
    """Format threat message with appropriate color coding"""
    color_map = {
        "CRITICAL": Colors.RED + Colors.BOLD,
        "HIGH": Colors.RED,
        "MEDIUM": Colors.YELLOW,
        "LOW": Colors.GREEN
    }
    
    color = color_map.get(severity, Colors.WHITE)
    return f"{color}[{severity}] {message}{Colors.RESET}"

def process_traffic_line(line, ai_detector, line_number, start_time):
    """
    Process a single line of traffic data with enhanced output
    
    Args:
        line (str): Traffic message to process
        ai_detector (AIDetector): AI detector instance
        line_number (int): Line number for logging
        start_time (float): Processing start time for timing
        
    Returns:
        dict: Processing results with detailed information
    """
    line = line.strip()
    if not line or line.startswith('#'):
        return None
    
    processing_start = time.time()
    
    # Run DFA pattern matching
    dfa_detections = check_all_patterns(line)
    
    # Run AI anomaly detection
    ai_anomaly = ai_detector.check_and_log(line)
    
    # Calculate processing time
    processing_time = time.time() - processing_start
    
    # Determine severity level
    severity = get_severity_level(dfa_detections, ai_anomaly)
    
    # Prepare detailed results
    result = {
        'line_number': line_number,
        'message': line,
        'dfa_detections': dfa_detections,
        'ai_anomaly': ai_anomaly,
        'threat_detected': bool(dfa_detections or ai_anomaly),
        'severity': severity,
        'processing_time': processing_time,
        'timestamp': datetime.datetime.now().isoformat()
    }
    
    # Enhanced logging with color coding
    logger.info(f"{Colors.CYAN}➤ Processing line {line_number}: {line}{Colors.RESET}")
    logger.info(f"   Processing time: {processing_time:.4f}s")
    
    if result['threat_detected']:
        alert_details = []
        if dfa_detections:
            alert_details.append(f"DFA Patterns: {', '.join(dfa_detections)}")
        if ai_anomaly:
            alert_details.append("AI Anomaly: DETECTED")
        
        threat_msg = format_threat_message(severity, " | ".join(alert_details))
        logger.warning(f"   {threat_msg}")
        
        # Additional context for critical threats
        if severity in ["CRITICAL", "HIGH"]:
            logger.warning(f"   {Colors.RED}⚠️  Immediate investigation recommended!{Colors.RESET}")
    else:
        logger.info(f"   {Colors.GREEN}✓ No threats detected{Colors.RESET}")
    
    logger.info(f"{Colors.WHITE}{'-' * 70}{Colors.RESET}")
    return result

def send_alert_to_api(result, alert_type):
    """Send detected threat to the API for storage with detailed context"""
    try:
        response = requests.post(
            'http://localhost:5000/alerts',
            json={
                'message': result['message'],
                'alert_type': alert_type,
                'severity': result['severity'].lower(),
                'line_number': result['line_number'],
                'line_content': result['message'],  # Using the original message content
                'detected_patterns': result['dfa_detections']
            }
        )
        if response.status_code == 201:
            logger.info(f"Alert sent to API: {result['message']} (Line {result['line_number']})")
        else:
            logger.warning(f"Failed to send alert to API: {response.status_code}")
    except requests.exceptions.RequestException as e:
        logger.error(f"API connection error: {e}")

def process_local_file(file_path):
    """
    Process traffic data from local file
    
    Args:
        file_path (str): Path to the traffic data file
    """
    try:
        # Load AI detector
        ai_detector = AIDetector("models/anomaly_model.pkl")
        logger.info("AI detector loaded successfully")
        
        # Read and process file
        with open(file_path, 'r') as file:
            lines = file.readlines()
        
        logger.info(f"Processing {len(lines)} lines from {file_path}")
        
        results = []
        overall_start = time.time()
        for i, line in enumerate(lines, 1):
            result = process_traffic_line(line, ai_detector, i, overall_start)
            if result:
                results.append(result)
                # Send threat to API if detected
                if result['threat_detected']:
                    alert_type = 'combined' if result['dfa_detections'] and result['ai_anomaly'] else (
                        'dfa' if result['dfa_detections'] else 'ai'
                    )
                    send_alert_to_api(result, alert_type)
                # Small delay to simulate processing
                time.sleep(0.1)
        
        # Generate summary
        threats_detected = sum(1 for r in results if r['threat_detected'])
        logger.info(f"Processing complete. Threats detected: {threats_detected}/{len(results)}")
        
        return results
        
    except FileNotFoundError:
        logger.error(f"File not found: {file_path}")
    except Exception as e:
        logger.error(f"Error processing file: {e}")

def main():
    """Main function to run the IDS orchestrator"""
    global logger
    logger = setup_logging()
    
    parser = argparse.ArgumentParser(description='AI-Driven Intrusion Detection System')
    parser.add_argument('--file', '-f', default='data/sample_traffic.txt',
                       help='Path to traffic data file (default: data/sample_traffic.txt)')
    parser.add_argument('--kafka', '-k', action='store_true',
                       help='Use Kafka streaming mode (requires Kafka server)')
    
    args = parser.parse_args()
    
    logger.info("Starting AI-Driven Intrusion Detection System")
    logger.info("=" * 60)
    
    if args.kafka:
        logger.info("Kafka mode selected")
        logger.info("Please run kafka_consumer.py in a separate terminal")
        logger.info("Then run kafka_producer.py to start streaming traffic")
    else:
        logger.info(f"Local file mode selected: {args.file}")
        process_local_file(args.file)
    
    logger.info("IDS Orchestrator completed")

if __name__ == "__main__":
    main()
