#!/usr/bin/env python3
"""
Test script to verify the audio transcription fixes work correctly.
"""

import os
import sys
import tempfile
import subprocess
import time
import requests
import json
from typing import Dict, Any

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'

def print_status(message: str, status: str = "INFO"):
    """Print colored status messages."""
    color_map = {
        "SUCCESS": Colors.GREEN,
        "ERROR": Colors.RED,
        "WARNING": Colors.YELLOW,
        "INFO": Colors.BLUE
    }
    color = color_map.get(status, Colors.BLUE)
    print(f"{color}[{status}] {message}{Colors.RESET}")

def check_dependencies():
    """Check if all required dependencies are installed."""
    print_status("Checking dependencies...", "INFO")
    
    required_packages = [
        'whisper',
        'torch',
        'transformers',
        'spacy',
        'fastapi',
        'uvicorn',
        'requests',
        'numpy'
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package)
            print_status(f"✅ {package}", "SUCCESS")
        except ImportError:
            print_status(f"❌ {package}", "ERROR")
            missing.append(package)
    
    if missing:
        print_status(f"Missing packages: {', '.join(missing)}", "ERROR")
        print_status("Install with: pip install -r requirements_fixed.txt", "WARNING")
        return False
    
    return True

def create_test_audio() -> str:
    """Create a simple test audio file."""
    print_status("Creating test audio file...", "INFO")
    
    try:
        import numpy as np
        import wave
        
        # Create a simple WAV file with a sine wave
        duration = 3  # 3 seconds
        sample_rate = 16000
        frequency = 440  # A4 note
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio_data = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)
        
        temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
        temp_file.close()
        
        with wave.open(temp_file.name, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        
        print_status(f"Created test audio: {temp_file.name}", "SUCCESS")
        return temp_file.name
        
    except Exception as e:
        print_status(f"Failed to create test audio: {e}", "ERROR")
        return None

def test_api_health() -> bool:
    """Test if the API is running and healthy."""
    print_status("Testing API health...", "INFO")
    
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            health_data = response.json()
            print_status("API is healthy", "SUCCESS")
            print_status(f"Health data: {json.dumps(health_data, indent=2)}", "INFO")
            return True
        else:
            print_status(f"API health check failed: {response.status_code}", "ERROR")
            return False
    except requests.exceptions.ConnectionError:
        print_status("Cannot connect to API server", "ERROR")
        return False
    except Exception as e:
        print_status(f"Health check error: {e}", "ERROR")
        return False

def test_audio_transcription(audio_path: str) -> bool:
    """Test audio transcription via API."""
    print_status("Testing audio transcription...", "INFO")
    
    try:
        with open(audio_path, 'rb') as f:
            files = {'file': ('test.wav', f, 'audio/wav')}
            response = requests.post(
                "http://localhost:8000/analyze/", 
                files=files, 
                timeout=30
            )
        
        if response.status_code == 200:
            data = response.json()
            print_status("✅ Transcription successful", "SUCCESS")
            print_status(f"Transcript: {data.get('transcript', 'No transcript')[:100]}...", "INFO")
            print_status(f"Entities: {len(data.get('entities', []))} found", "INFO")
            print_status(f"Difficulty: {data.get('difficulty', 'Unknown')}", "INFO")
            return True
        else:
            error_detail = response.json().get('detail', 'Unknown error')
            print_status(f"Transcription failed: {response.status_code} - {error_detail}", "ERROR")
            return False
            
    except Exception as e:
        print_status(f"Transcription test error: {e}", "ERROR")
        return False

def start_api_server() -> subprocess.Popen:
    """Start the API server in background."""
    print_status("Starting API server...", "INFO")
    
    try:
        process = subprocess.Popen([
            sys.executable, 
            "test_fixed.py", 
            "api"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a bit for server to start
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print_status("API server started successfully", "SUCCESS")
            return process
        else:
            stdout, stderr = process.communicate()
            print_status("Failed to start API server", "ERROR")
            print_status(f"stdout: {stdout.decode()}", "ERROR")
            print_status(f"stderr: {stderr.decode()}", "ERROR")
            return None
            
    except Exception as e:
        print_status(f"Error starting API server: {e}", "ERROR")
        return None

def main():
    """Main test function."""
    print_status("=== Educational Video Tagging API Test Suite ===", "INFO")
    
    # Step 1: Check dependencies
    if not check_dependencies():
        print_status("Please install missing dependencies and try again", "ERROR")
        return False
    
    # Step 2: Create test audio
    test_audio = create_test_audio()
    if not test_audio:
        print_status("Cannot proceed without test audio", "ERROR")
        return False
    
    # Step 3: Start API server
    api_process = start_api_server()
    if not api_process:
        print_status("Cannot proceed without API server", "ERROR")
        return False
    
    try:
        # Step 4: Test API health
        if not test_api_health():
            print_status("API health check failed", "ERROR")
            return False
        
        # Step 5: Test transcription
        success = test_audio_transcription(test_audio)
        
        if success:
            print_status("🎉 All tests passed! The API is working correctly.", "SUCCESS")
        else:
            print_status("❌ Transcription test failed", "ERROR")
        
        return success
        
    finally:
        # Clean up
        if api_process and api_process.poll() is None:
            print_status("Stopping API server...", "INFO")
            api_process.terminate()
            api_process.wait()
        
        if os.path.exists(test_audio):
            os.unlink(test_audio)
            print_status("Cleaned up test audio file", "INFO")

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
