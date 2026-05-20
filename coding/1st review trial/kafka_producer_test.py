import time
import json
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def main():
    logger = setup_logging()
    logs = [
        "normal traffic",
        "attack detected",
        "scan attempt",
        "user login",
        "unauthorized access"
    ]
    for i, log in enumerate(logs, 1):
        message = {
            "timestamp": time.time(),
            "message": log,
            "source": "test_producer",
            "sequence": i
        }
        logger.info(f"Produced (simulated): {json.dumps(message)}")
        time.sleep(0.5)

if __name__ == "__main__":
    main()
