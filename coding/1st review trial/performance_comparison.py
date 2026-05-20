"""
Performance comparison script to demonstrate efficiency improvements
"""

import time
import numpy as np
from ai_module import AIDetector, create_sample_training_data

def time_function(func, *args, **kwargs):
    """Time a function execution"""
    start = time.time()
    result = func(*args, **kwargs)
    end = time.time()
    return result, end - start

def performance_test():
    """Run performance tests on the optimized AI module"""
    print("AI Module Performance Analysis")
    print("=" * 50)
    
    # Create test data
    training_data = create_sample_training_data()
    test_messages = [
        "normal traffic flow",
        "attack detected in system",
        "user authentication successful",
        "scan attempt from external IP",
        "database query executed successfully",
        "unauthorized access attempt blocked",
        "system health check completed",
        "malware signature detected",
        "network traffic analysis complete",
        "security policy violation detected"
    ] * 10  # 100 test messages
    
    print(f"Training data size: {len(training_data)} samples")
    print(f"Test data size: {len(test_messages)} messages")
    print()
    
    # Test 1: Model initialization and training
    print("Test 1: Model Training Performance")
    print("-" * 30)
    
    detector, training_time = time_function(lambda: AIDetector())
    print(f"Model initialization: {training_time:.4f} seconds")
    
    _, training_fit_time = time_function(detector.train, training_data)
    print(f"Model training: {training_fit_time:.4f} seconds")
    print(f"Training throughput: {len(training_data)/training_fit_time:.1f} samples/second")
    print()
    
    # Test 2: Individual predictions
    print("Test 2: Individual Prediction Performance")
    print("-" * 40)
    
    individual_times = []
    for message in test_messages[:10]:  # Test first 10 messages
        _, pred_time = time_function(detector.predict, message)
        individual_times.append(pred_time)
    
    avg_individual_time = np.mean(individual_times)
    print(f"Average individual prediction time: {avg_individual_time:.6f} seconds")
    print(f"Individual prediction throughput: {1/avg_individual_time:.1f} predictions/second")
    print()
    
    # Test 3: Batch predictions (if available)
    print("Test 3: Batch Prediction Performance")
    print("-" * 35)
    
    if hasattr(detector, 'predict_batch'):
        batch_messages = test_messages[:50]  # Test with 50 messages
        _, batch_time = time_function(detector.predict_batch, batch_messages)
        print(f"Batch prediction time (50 messages): {batch_time:.4f} seconds")
        print(f"Batch prediction throughput: {len(batch_messages)/batch_time:.1f} predictions/second")
        print(f"Speedup vs individual: {(avg_individual_time * len(batch_messages))/batch_time:.2f}x")
    else:
        print("Batch prediction not available")
    print()
    
    # Test 4: Feature extraction performance
    print("Test 4: Feature Extraction Performance")
    print("-" * 38)
    
    feature_times = []
    for message in test_messages[:20]:
        _, feat_time = time_function(detector.extract_features, message)
        feature_times.append(feat_time)
    
    avg_feature_time = np.mean(feature_times)
    print(f"Average feature extraction time: {avg_feature_time:.6f} seconds")
    print(f"Feature extraction throughput: {1/avg_feature_time:.1f} extractions/second")
    print()
    
    # Test 5: Memory efficiency analysis
    print("Test 5: Memory Usage Analysis")
    print("-" * 28)
    
    # Test with different batch sizes
    batch_sizes = [10, 50, 100, 200]
    for batch_size in batch_sizes:
        if len(test_messages) >= batch_size:
            batch_subset = test_messages[:batch_size]
            if hasattr(detector, 'predict_batch'):
                _, batch_time = time_function(detector.predict_batch, batch_subset)
                throughput = batch_size / batch_time
                print(f"Batch size {batch_size:3d}: {throughput:6.1f} predictions/second")
    
    print()
    print("Performance Summary:")
    print(f"• Training: {len(training_data)/training_fit_time:.1f} samples/second")
    print(f"• Individual predictions: {1/avg_individual_time:.1f} predictions/second")
    print(f"• Feature extraction: {1/avg_feature_time:.1f} extractions/second")
    if hasattr(detector, 'predict_batch'):
        print(f"• Batch predictions: Up to {len(batch_messages)/batch_time:.1f} predictions/second")
    
    print("\nOptimizations implemented:")
    print("• Single-pass character analysis in feature extraction")
    print("• Pre-allocated NumPy arrays for better memory efficiency")
    print("• Reduced memory allocations and list comprehensions")
    print("• Float32 precision for reduced memory usage")
    print("• Batch processing capabilities for bulk operations")
    print("• Optimized logging (debug-level feature logging)")

if __name__ == "__main__":
    performance_test()
