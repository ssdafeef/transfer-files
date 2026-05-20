"""
Enhanced IDS Data Generator
Generates realistic security events and traffic for testing the Streamlit dashboard
"""

import requests
import time
import random
import json
from datetime import datetime, timedelta
import threading
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IDSDataGenerator:
    def __init__(self, api_url="http://localhost:5000"):
        self.api_url = api_url
        self.running = False
        
        # Realistic traffic patterns
        self.normal_traffic = [
            "user login successful",
            "file accessed successfully",
            "database query executed",
            "connection established",
            "authentication passed",
            "session started",
            "backup completed",
            "system health check",
            "network traffic normal",
            "cache updated",
            "load balanced",
            "encryption enabled",
            "synchronization done",
            "https request to api.example.com",
            "ssh connection from 192.168.1.100",
            "vpn connection established",
            "jwt token validation passed",
            "two-factor authentication enabled"
        ]
        
        self.attack_patterns = [
            ("attack detected in system", "attack", "high"),
            ("unauthorized access attempt", "unauthorized access", "high"),
            ("scan attempt detected", "scan attempt", "medium"),
            ("malware infection detected", "malware", "critical"),
            ("sql injection attempt", "injection", "high"),
            ("bruteforce attack in progress", "bruteforce", "high"),
            ("ddos attack ongoing", "ddos", "critical"),
            ("phishing attempt detected", "phishing", "medium"),
            ("privilege escalation attempt", "attack", "critical"),
            ("data exfiltration detected", "attack", "critical"),
            ("ransomware detected", "malware", "critical"),
            ("zero-day exploit attempt", "attack", "critical")
        ]
    
    def check_api_health(self):
        """Check if API is available"""
        try:
            response = requests.get(f"{self.api_url}/health", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def send_alert(self, message, alert_type, severity, patterns=None):
        """Send an alert to the API"""
        try:
            payload = {
                "message": message,
                "alert_type": alert_type,
                "severity": severity,
                "line_number": random.randint(1, 1000),
                "line_content": message,
                "detected_patterns": patterns or []
            }
            
            response = requests.post(
                f"{self.api_url}/alerts",
                json=payload,
                timeout=5
            )
            
            if response.status_code == 201:
                logger.info(f"Alert sent: [{severity.upper()}] {message}")
                return True
            else:
                logger.warning(f"Failed to send alert: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error sending alert: {e}")
            return False
    
    def generate_normal_traffic(self):
        """Generate normal traffic events"""
        message = random.choice(self.normal_traffic)
        
        # Sometimes add variations
        if random.random() < 0.3:
            variations = [
                f"{message} at {datetime.now().strftime('%H:%M:%S')}",
                f"{message} from user {random.randint(1, 100)}",
                f"{message} - session {random.randint(1000, 9999)}"
            ]
            message = random.choice(variations)
        
        # Normal traffic occasionally generates low-severity alerts for monitoring
        if random.random() < 0.1:  # 10% chance
            return self.send_alert(message, "ai", "low", [])
        
        return True
    
    def generate_attack_event(self):
        """Generate attack/threat events"""
        attack_data = random.choice(self.attack_patterns)
        message, pattern, severity = attack_data
        
        # Add some variation to attack messages
        variations = [
            message,
            f"{message} from IP 192.168.1.{random.randint(1, 254)}",
            f"Multiple {message.lower()}",
            f"{message} - {random.choice(['immediate action required', 'investigating', 'blocked'])}"
        ]
        
        final_message = random.choice(variations)
        alert_type = "dfa" if pattern in ["attack", "scan attempt"] else random.choice(["dfa", "ai", "combined"])
        
        return self.send_alert(final_message, alert_type, severity, [pattern])
    
    def generate_realistic_scenario(self):
        """Generate realistic security scenarios"""
        scenarios = [
            # Normal operation period
            {
                "duration": 30,  # seconds
                "normal_rate": 0.8,  # 80% normal traffic
                "attack_rate": 0.05,  # 5% attacks
                "description": "Normal Operation"
            },
            # Scan attempt period
            {
                "duration": 15,
                "normal_rate": 0.6,
                "attack_rate": 0.3,
                "attack_focus": ["scan attempt", "unauthorized access"],
                "description": "Scanning Activity Detected"
            },
            # Attack period
            {
                "duration": 20,
                "normal_rate": 0.4,
                "attack_rate": 0.4,
                "attack_focus": ["attack", "bruteforce", "injection"],
                "description": "Active Attack in Progress"
            },
            # Critical incident
            {
                "duration": 10,
                "normal_rate": 0.2,
                "attack_rate": 0.6,
                "attack_focus": ["malware", "ddos", "attack"],
                "description": "Critical Security Incident"
            }
        ]
        
        scenario = random.choice(scenarios)
        logger.info(f"🎭 Starting scenario: {scenario['description']} (Duration: {scenario['duration']}s)")
        
        start_time = time.time()
        while time.time() - start_time < scenario['duration'] and self.running:
            # Determine event type
            rand = random.random()
            
            if rand < scenario['normal_rate']:
                self.generate_normal_traffic()
            elif rand < scenario['normal_rate'] + scenario['attack_rate']:
                # Focus on specific attack types if specified
                if 'attack_focus' in scenario:
                    focused_attacks = [
                        attack for attack in self.attack_patterns
                        if attack[1] in scenario['attack_focus']
                    ]
                    if focused_attacks:
                        attack_data = random.choice(focused_attacks)
                        message, pattern, severity = attack_data
                        self.send_alert(message, "dfa", severity, [pattern])
                    else:
                        self.generate_attack_event()
                else:
                    self.generate_attack_event()
            
            # Variable sleep time to simulate real network traffic
            sleep_time = random.uniform(0.5, 3.0)
            time.sleep(sleep_time)
        
        logger.info(f"✅ Completed scenario: {scenario['description']}")
    
    def start_continuous_generation(self):
        """Start continuous data generation"""
        self.running = True
        logger.info("🚀 Starting continuous IDS data generation...")
        
        # Check API availability
        if not self.check_api_health():
            logger.error("❌ API server not available. Please start api.py first.")
            return
        
        logger.info("✅ API server is available")
        
        try:
            while self.running:
                # Run a realistic scenario
                self.generate_realistic_scenario()
                
                # Brief pause between scenarios
                if self.running:
                    pause_time = random.uniform(5, 15)
                    logger.info(f"⏸️  Pausing for {pause_time:.1f} seconds before next scenario...")
                    time.sleep(pause_time)
                
        except KeyboardInterrupt:
            logger.info("🛑 Data generation stopped by user")
        except Exception as e:
            logger.error(f"❌ Error in data generation: {e}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop data generation"""
        self.running = False
        logger.info("🛑 Stopping data generation...")

def main():
    """Main function"""
    print("🛡️  IDS Data Generator")
    print("=" * 40)
    print("This script generates realistic security events for testing the dashboard.")
    print("Make sure the API server (api.py) is running before starting this.")
    print()
    
    generator = IDSDataGenerator()
    
    try:
        generator.start_continuous_generation()
    except KeyboardInterrupt:
        print("\n🛑 Stopping data generation...")
        generator.stop()
    
    print("👋 Data generation stopped.")

if __name__ == "__main__":
    main()