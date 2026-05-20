"""
AI Module for Anomaly-based Intrusion Detection
Uses scikit-learn's Isolation Forest for unsupervised anomaly detection
"""

import logging
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

class AIDetector:
    """
    AI-based anomaly detector using Isolation Forest algorithm
    """
    
    def __init__(self, model_path=None):
        """
        Initialize AI detector
        
        Args:
            model_path (str, optional): Path to pre-trained model. If None, creates new model
        """
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        
        if model_path:
            try:
                model_data = joblib.load(model_path)
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.logger.info(f"Loaded pre-trained model and scaler from {model_path}")
            except FileNotFoundError:
                self.logger.warning(f"Model file {model_path} not found, creating new model")
                self.model = IsolationForest(contamination=0.1, random_state=42)
        else:
            self.model = IsolationForest(contamination=0.12, random_state=42)
            self.logger.info("Created new Isolation Forest model")

    def extract_features(self, text):
        """
        Extract features from text for anomaly detection (optimized version)
        
        Args:
            text (str): Input text to extract features from
            
        Returns:
            numpy.ndarray: Array of extracted features
        """
        # Single pass through text for character-based features
        text_len = len(text)
        if text_len == 0:
            return np.zeros(10)
        
        # Character analysis in single pass
        digit_count = 0
        special_count = 0
        upper_count = 0
        lower_count = 0
        unique_chars = set()
        
        for char in text:
            unique_chars.add(char.lower())
            if char.isdigit():
                digit_count += 1
            elif not char.isalnum():
                special_count += 1
            elif char.isupper():
                upper_count += 1
            elif char.islower():
                lower_count += 1
        
        # Word analysis
        words = text.split()
        word_count = len(words)
        
        if word_count == 0:
            avg_word_len = 0
            long_words_count = 0
            alpha_words_count = 0
        else:
            word_lengths = [len(word) for word in words]
            avg_word_len = sum(word_lengths) / word_count
            long_words_count = sum(1 for length in word_lengths if length > 6)
            alpha_words_count = sum(1 for word in words if word.isalpha())
        
        # Build feature array directly
        features = np.array([
            text_len,                     # Length of the message
            digit_count,                  # Number of digits
            special_count,                # Number of special characters
            upper_count,                  # Number of uppercase letters
            lower_count,                  # Number of lowercase letters
            word_count,                   # Number of words
            len(unique_chars),            # Number of unique characters
            avg_word_len,                 # Average word length
            long_words_count,             # Number of long words
            alpha_words_count             # Number of alphabetic words
        ], dtype=np.float32)
        
        return features

    def train(self, X_train):
        """
        Train the anomaly detection model (optimized version)
        
        Args:
            X_train (list): List of training samples (text strings)
        """
        if not X_train:
            self.logger.warning("No training data provided")
            return
            
        # Pre-allocate feature array for better memory efficiency
        num_samples = len(X_train)
        features_array = np.zeros((num_samples, 10), dtype=np.float32)
        
        # Extract features in batch for efficiency
        for i, text in enumerate(X_train):
            features_array[i] = self.extract_features(text)
        
        # Scale the features
        self.scaler.fit(features_array)
        scaled_features = self.scaler.transform(features_array)
        
        # Train the model
        self.model.fit(scaled_features)
        self.logger.info(f"AI model training completed on {num_samples} samples")

    def predict(self, text):
        """
        Predict if the input text is anomalous (optimized version)
        
        Args:
            text (str): Input text to check for anomalies
            
        Returns:
            int: -1 for anomaly, 1 for normal
        """
        features = self.extract_features(text)
        # Reshape for single sample prediction
        scaled_features = self.scaler.transform(features.reshape(1, -1))
        prediction = self.model.predict(scaled_features)[0]
        
        if prediction == -1:
            self.logger.warning(f"[AI ALERT] Anomaly detected in: {text}")
            # Only log features in debug mode to reduce overhead
            if self.logger.isEnabledFor(logging.DEBUG):
                self.logger.debug(f"Features: {features}")
        
        return prediction

    def check_and_log(self, text):
        """
        Check for anomalies and log if detected
        
        Args:
            text (str): Input text to check
            
        Returns:
            bool: True if anomaly detected, False otherwise
        """
        return self.predict(text) == -1

    def predict_batch(self, texts):
        """
        Predict anomalies for multiple texts efficiently
        
        Args:
            texts (list): List of input texts to check for anomalies
            
        Returns:
            numpy.ndarray: Array of predictions (-1 for anomaly, 1 for normal)
        """
        if not texts:
            return np.array([])
            
        # Pre-allocate feature array
        num_texts = len(texts)
        features_array = np.zeros((num_texts, 10), dtype=np.float32)
        
        # Extract features in batch
        for i, text in enumerate(texts):
            features_array[i] = self.extract_features(text)
        
        # Scale and predict in batch
        scaled_features = self.scaler.transform(features_array)
        predictions = self.model.predict(scaled_features)
        
        # Log anomalies
        for i, (text, prediction) in enumerate(zip(texts, predictions)):
            if prediction == -1:
                self.logger.warning(f"[AI ALERT] Anomaly detected in: {text}")
                if self.logger.isEnabledFor(logging.DEBUG):
                    self.logger.debug(f"Features: {features_array[i]}")
        
        return predictions

    def save(self, path):
        """
        Save the trained model and scaler to file
        
        Args:
            path (str): Path to save the model
        """
        model_data = {
            'model': self.model,
            'scaler': self.scaler
        }
        joblib.dump(model_data, path)
        self.logger.info(f"Model and scaler saved to {path}")


def create_sample_training_data():
    """
    Create enhanced sample training data for the AI model (optimized version)
    Includes more diverse normal patterns and edge cases

    Returns:
        list: List of normal traffic samples for training
    """
    # Use tuple for memory efficiency, then convert to list
    base_patterns = (
        # Normal traffic patterns
        "normal traffic", "normal traffic flow", "user login", "user login successful",
        "file accessed", "file accessed successfully", "connection established",
        "system operation normal", "data transfer complete", "authentication passed",
        "session started", "request processed", "response sent", "response sent successfully",
        "operation completed", "service running", "service running normally",
        "status check", "status check completed", "monitoring active", "log entry created",
        "network traffic normal", "system health check", "backup completed",
        "update installed", "configuration saved",
        
        # More diverse normal patterns
        "database query executed", "cache updated", "load balanced", "security scan clean",
        "firewall rule applied", "encryption enabled", "compression complete",
        "synchronization done", "replication successful", "maintenance window started",
        
        # Include some variations that might be considered normal
        "error reported", "connection reset", "system reboot", "connection timeout",
        "session expired", "password reset requested", "account lockout",
        "certificate expired", "log rotation", "backup verification",
        
        # Additional normal patterns from enhanced dataset
        "https request to api.example.com", "ssh connection from 192.168.1.100",
        "database query from application server", "file upload to cloud storage",
        "email sent via smtp server", "dns lookup for google.com",
        "vpn connection established", "load balancer health check", "cdn cache refresh",
        "api rate limit exceeded", "session timeout occurred", "cookie authentication successful",
        "jwt token validation passed", "oauth2 authorization completed",
        "two-factor authentication enabled",
        
        # Edge cases that should be considered normal
        "partial operation completed", "temporary system slowdown", "network congestion detected",
        "resource allocation adjusted", "security policy updated", "access control modified",
        "firewall configuration changed", "system update available", "certificate expiration warning",
        "log rotation completed", "backup verification failed but retrying",
        "high cpu utilization during maintenance", "memory usage spike during backup",
        "network bandwidth exceeded temporarily",
        
        # Realistic operational messages
        "application deployed successfully", "microservice health check passed",
        "container orchestration completed", "kubernetes pod started", "docker container running",
        "cloud instance provisioned", "virtual machine migrated", "storage volume expanded",
        "network interface configured", "dns record updated", "ssl certificate installed",
        "security patch applied", "vulnerability scan completed", "compliance check passed",
        "audit trail generated",
        
        # Multi-word normal patterns
        "user authentication successful with two factor",
        "database connection pool established successfully",
        "network load balancer health check passed",
        "cloud storage bucket created with encryption",
        "api gateway request processed normally",
        "message queue consumer started processing",
        "event stream processing completed successfully",
        "batch job execution finished without errors",
        "scheduled task ran as expected",
        "cron job completed successfully"
    )
    
    return list(base_patterns)


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create and train a sample model
    detector = AIDetector()
    training_data = create_sample_training_data()
    detector.train(training_data)
    
    # Test the model
    test_cases = [
        "normal traffic",           # Should be normal
        "attack detected",          # Should be anomaly
        "unauthorized access",      # Should be anomaly  
        "user login",               # Should be normal
        "scan attempt detected"     # Should be anomaly
    ]
    
    for test in test_cases:
        result = detector.predict(test)
        status = "ANOMALY" if result == -1 else "NORMAL"
        print(f"{test} -> {status}")
    
    # Save the model
    detector.save("models/anomaly_model.pkl")
