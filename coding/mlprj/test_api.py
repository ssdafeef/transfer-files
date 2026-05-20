#!/usr/bin/env python3
"""
Test script for the Educational Video Tagging API
"""

import requests
import json
import os
import tempfile

def test_api_health():
    """Test if the API is running."""
    try:
        response = requests.get("http://localhost:8000/docs")
        if response.status_code == 200:
            print("✅ API is running and accessible")
            return True
        else:
            print(f"❌ API returned status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        return False

def test_analyze_endpoint():
    """Test the /analyze/ endpoint with a sample audio file."""
    # Create a simple test audio file (or use a mock)
    test_audio_path = "test_audio.mp3"
    
    # For testing purposes, we'll create a minimal test
    # In a real scenario, you'd use an actual audio file
    
    if not os.path.exists(test_audio_path):
        print("⚠️  No test audio file found. Creating a placeholder...")
        # This is a placeholder - in real testing, use actual audio
        return
    
    try:
        with open(test_audio_path, 'rb') as f:
            files = {'file': ('test_audio.mp3', f, 'audio/mpeg')}
            response = requests.post("http://localhost:8000/analyze/", files=files)
            
        if response.status_code == 200:
            result = response.json()
            print("✅ /analyze/ endpoint working correctly")
            print("📊 Results preview:")
            print(f"   Transcript length: {len(result.get('transcript', ''))} chars")
            print(f"   Entities found: {len(result.get('entities', []))}")
            print(f"   Topic keywords: {len(result.get('topic_keywords', []))}")
            print(f"   Difficulty: {result.get('difficulty', 'Unknown')}")
            return True
        else:
            print(f"❌ /analyze/ endpoint failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to API server")
        return False
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        return False

def main():
    """Run all API tests."""
    print("🧪 Testing Educational Video Tagging API...")
    print("=" * 50)
    
    # Test 1: API Health
    print("\n1. Testing API Health...")
    api_running = test_api_health()
    
    if api_running:
        print("\n2. Testing /analyze/ endpoint...")
        test_analyze_endpoint()
    else:
        print("\n⚠️  API not running. Please start it with: python test.py api")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main()
