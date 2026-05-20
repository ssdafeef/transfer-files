# AI-Driven Intrusion Detection System (IDS)

A Python-based Intrusion Detection System that combines signature-based detection (DFA engine) with anomaly detection (AI/ML module) for comprehensive security monitoring.

## Features

- **DFA Engine**: Signature-based intrusion detection using Deterministic Finite Automata
- **AI/ML Module**: Anomaly detection using scikit-learn's Isolation Forest
- **Kafka Integration**: Real-time streaming with Kafka producer and consumer
- **Dual Operation Modes**: Local file processing and Kafka streaming
- **Comprehensive Logging**: Clear alerts for DFA matches and AI anomalies
- **REST API**: Alert management API for integration with other systems
- **Enhanced Output**: Color-coded severity levels and detailed threat analysis
- **Expanded Detection**: 8+ DFA patterns covering common attack types

## Project Structure

```
ids/
├── ai_module.py          # AI/ML anomaly detection module
├── dfa_engine.py         # DFA engine for signature-based detection
├── kafka_producer.py     # Kafka producer for traffic streaming
├── kafka_consumer.py     # Kafka consumer for real-time processing
├── main.py               # Main orchestrator (local + Kafka modes)
├── requirements.txt      # Python dependencies
├── data/
│   └── sample_traffic.txt # Sample traffic data
└── README.md             # This file
```

## Prerequisites

- Python 3.10+
- Kafka (for streaming mode)
- pip package manager

## Installation

1. Clone or download this repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. For Kafka mode, ensure Kafka is running locally on port 9092

## Usage

### Local Mode (No Kafka Required)
```bash
python main.py
```

Processes `data/sample_traffic.txt` directly and outputs detection results.

### Kafka Mode (Requires Kafka)
1. Start Kafka server
2. Run the consumer:
   ```bash
   python kafka_consumer.py
   ```
3. Run the producer:
   ```bash
   python kafka_producer.py
   ```

### Training the AI Model
The AI module includes a pre-trained model (`models/anomaly_model.pkl`). To retrain:
```python
from ai_module import AIDetector
# Create and train new model
detector = AIDetector()
detector.train(training_data)
detector.save("models/anomaly_model.pkl")
```

## DFA Patterns

The system currently detects these patterns:
- "attack" - Basic attack pattern detection
- "unauthorized" - Unauthorized access attempts
- "scan" - Scanning activities

## AI Features

The AI module extracts these features for anomaly detection:
- Message length
- Number of digits in message
- Special character count
- Uppercase/lowercase ratio

## Extension Ideas

1. **Additional DFA Patterns**: Add more intrusion signatures
2. **Enhanced AI Features**: Add more sophisticated feature extraction
3. **Database Integration**: Store alerts in a database
4. **Web Interface**: Add a dashboard for monitoring
5. **Real-time Alerts**: Integrate with notification systems
6. **Multiple Kafka Topics**: Support different traffic types
7. **Performance Monitoring**: Add metrics and performance tracking
8. **Docker Support**: Containerize the application

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - feel free to use this project for learning and development purposes.
