"""
Kafka Consumer for IDS Real-time Processing
Consumes traffic from Kafka topic and runs DFA + AI detection
"""

from confluent_kafka import Consumer, KafkaException
import json
import logging
from dfa_engine import check_all_patterns
from ai_module import AIDetector

def setup_logging():
    """Configure logging for the consumer"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def main():
    """Main function to run the Kafka consumer"""
    logger = setup_logging()
    
    # Kafka configuration
    bootstrap_servers = 'localhost:9092'
    topic = 'traffic'
    
    try:
        # Create Kafka consumer
        consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': 'ids-consumer-group',
            'auto.offset.reset': 'earliest'
        })
        
        consumer.subscribe([topic])
        
        logger.info(f"Kafka consumer connected to {bootstrap_servers}, topic: {topic}")
        logger.info("Waiting for traffic messages...")
        
        # Load AI detector
        ai_detector = AIDetector("models/anomaly_model.pkl")
        logger.info("AI detector loaded successfully")
        
        # Process messages
        while True:
            try:
                msg = consumer.poll(timeout=1.0)
                
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaException._PARTITION_EOF:
                        continue
                    else:
                        logger.error(f"Kafka error: {msg.error()}")
                        continue
                
                try:
                    message_data = json.loads(msg.value().decode('utf-8'))
                    log_message = message_data.get("message", "")
                    timestamp = message_data.get("timestamp", "")
                    source = message_data.get("source", "")
                    
                    logger.info(f"Received [{source}] {log_message}")
                    
                    # Run DFA pattern matching
                    dfa_detections = check_all_patterns(log_message)
                    
                    # Run AI anomaly detection
                    ai_anomaly = ai_detector.check_and_log(log_message)
                    
                    # Log summary
                    if dfa_detections or ai_anomaly:
                        alert_summary = []
                        if dfa_detections:
                            alert_summary.append(f"DFA: {', '.join(dfa_detections)}")
                        if ai_anomaly:
                            alert_summary.append("AI: Anomaly detected")
                        
                        logger.warning(f"[SECURITY ALERT] {', '.join(alert_summary)}")
                    else:
                        logger.info("No threats detected")
                        
                    logger.info("-" * 50)
                    
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    continue
                    
            except KeyboardInterrupt:
                logger.info("Consumer interrupted by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                break
                
    except Exception as e:
        logger.error(f"Error in Kafka consumer: {e}")
    finally:
        if 'consumer' in locals():
            consumer.close()
            logger.info("Kafka consumer closed")

if __name__ == "__main__":
    main()
