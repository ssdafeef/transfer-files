import requests

def test_alerts_api():
    """Test the alerts API integration with enhanced output"""
    try:
        # Get all alerts
        response = requests.get('http://localhost:5000/alerts')
        data = response.json()
        
        print(f"Total alerts stored: {data['count']}")
        print("Alerts retrieved from API:")
        print("-" * 80)
        
        for i, alert in enumerate(data['alerts']):
            print(f"{i+1}. {alert['message']}")
            print(f"   Severity: {alert['severity']}")
            print(f"   Type: {alert['alert_type']}")
            if alert.get('line_number'):
                print(f"   Line: {alert['line_number']}")
            if alert.get('line_content'):
                print(f"   Content: {alert['line_content']}")
            if alert.get('detected_patterns'):
                print(f"   Patterns: {', '.join(alert['detected_patterns'])}")
            print(f"   Timestamp: {alert['timestamp']}")
            print()
            
        # Test health endpoint
        health_response = requests.get('http://localhost:5000/health')
        health_data = health_response.json()
        print(f"Health check: {health_data['status']}")
        print(f"Alerts count: {health_data['alerts_count']}")
        
    except requests.exceptions.RequestException as e:
        print(f"API connection error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_alerts_api()
