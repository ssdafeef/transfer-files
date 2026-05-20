#!/usr/bin/env python3
"""
Direct testing of the Educational Video Tagging system functions
"""

import sys
import os
import tempfile
import subprocess
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_basic_functionality():
    """Test basic functionality without API."""
    print("🧪 Testing Direct Functionality...")
    print("=" * 50)
    
    try:
        import test
        
        # Test 1: Check if all modules can be imported
        print("\n1. Testing module imports...")
        print("   ✅ test.py imported successfully")
        
        # Test 2: Test text processing functions
        print("\n2. Testing text processing functions...")
        
        # Test extract_entities
        sample_text = "Apple Inc. was founded by Steve Jobs in Cupertino, California."
        entities = test.extract_entities(sample_text)
        print(f"   ✅ extract_entities: {entities}")
        
        # Test predict_difficulty
        difficulty = test.predict_difficulty(sample_text)
        print(f"   ✅ predict_difficulty: {difficulty}")
        
        # Test extract_features
        features = test.extract_features(sample_text)
        print(f"   ✅ extract_features: {features}")
        
        # Test embed_text
        embedding = test.embed_text(sample_text)
        if embedding:
            print(f"   ✅ embed_text: Vector of length {len(embedding)}")
        else:
            print("   ⚠️  embed_text: Not available (transformers not loaded)")
        
        # Test BERTopic functions
        if test.BERTOPIC_AVAILABLE:
            print("   ✅ BERTopic available")
            topics, probs = test.fit_bertopic([sample_text])
            print(f"   ✅ fit_bertopic: topics={topics}, probs={probs}")
        else:
            print("   ⚠️  BERTopic not available")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing direct functionality: {e}")
        return False

def test_api_startup():
    """Test API startup process."""
    print("\n3. Testing API startup...")
    
    try:
        # Start API in background
        process = subprocess.Popen(
            [sys.executable, "test.py", "api"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for startup
        time.sleep(3)
        
        # Check if process is still running
        if process.poll() is None:
            print("   ✅ API server started successfully")
            process.terminate()
            process.wait()
            return True
        else:
            stdout, stderr = process.communicate()
            print(f"❌ API failed to start: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error starting API: {e}")
        return False

def create_sample_audio():
    """Create a sample audio file for testing."""
    print("\n4. Creating sample audio file...")
    
    try:
        # Create a simple text file as placeholder
        with open("sample_text.txt", "w") as f:
            f.write("This is a sample educational content about machine learning and artificial intelligence.")
        
        print("   ✅ Sample text file created")
        return True
    except Exception as e:
        print(f"❌ Error creating sample: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Comprehensive Testing of Educational Video Tagging System")
    print("=" * 60)
    
    # Test 1: Basic functionality
    basic_ok = test_basic_functionality()
    
    # Test 2: API startup
    api_ok = test_api_startup()
    
    # Test 3: Sample creation
    sample_ok = create_sample_audio()
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print(f"   Basic functionality: {'✅ PASS' if basic_ok else '❌ FAIL'}")
    print(f"   API startup: {'✅ PASS' if api_ok else '❌ FAIL'}")
    print(f"   Sample creation: {'✅ PASS' if sample_ok else '❌ FAIL'}")
    
    if basic_ok and api_ok:
        print("\n🎉 System is ready for use!")
        print("\nTo use the system:")
        print("1. Start API: python test.py api")
        print("2. In new terminal, run Streamlit: streamlit run test.py")
    else:
        print("\n⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()
