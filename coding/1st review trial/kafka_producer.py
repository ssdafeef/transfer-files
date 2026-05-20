"""
Kafka Producer for IDS Traffic Streaming
Reads traffic data from file and sends to Kafka topic for real-time processing
"""

from confluent_kafka import Producer
import time
import json
import logging

def delivery_report(err, msg):
    """Callback function for message delivery reports"""
    if err is not None:
        logging.error(f"Message delivery failed: {err}")
    else:
        logging.info(f"Message delivered to {msg.topic()} [{msg.partition()}]")

def setup_logging():
    """Configure logging for the producer"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def read_traffic_data(file_path):
    """
    Read traffic data from file
    
    Args:
        file_path (str): Path to the traffic data file
        
    Returns:
        list: List of traffic messages
    """
    try:
        with open(file_path, 'r') as file:
            traffic_data = [line.strip() for line in file if line.strip()]
        return traffic_data
    except FileNotFoundError:
        logger.error(f"Traffic data file not found: {file_path}")
        return []

def main():
    """Main function to run the Kafka producer"""
    global logger
    logger = setup_logging()
    
    # Kafka configuration
    bootstrap_servers = 'localhost:9092'
    topic = 'traffic'
    
    try:
        # Create Kafka producer
        producer = Producer({
            'bootstrap.servers': bootstrap_servers
        })
        
        logger.info(f"Kafka producer connected to {bootstrap_servers}")
        
        # Read traffic data
        traffic_data = read_traffic_data('data/sample_traffic.txt')
        if not traffic_data:
            logger.error("No traffic data found. Exiting.")
            return
        
        logger.info(f"Loaded {len(traffic_data)} traffic messages")
        
        # Send traffic messages to Kafka
        for i, message in enumerate(traffic_data, 1):
            kafka_message = {
                "timestamp": time.time(),
                "message": message,
                "source": "sample_traffic",
                "sequence": i
            }
            
            producer.produce(topic, json.dumps(kafka_message), callback=delivery_report)
            logger.info(f"Produced: {message}")
            
            # Add small delay to simulate real-time traffic
            time.sleep(0.5)
        
        # Flush and close producer
        producer.flush()
        logger.info("All messages sent successfully")
        
    except Exception as e:
        logger.error(f"Error in Kafka producer: {e}")

if __name__ == "__main__":
    main()
