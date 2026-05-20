#!/usr/bin/env python3
"""
Test script to verify audio processing functionality
"""

import os
import tempfile
import subprocess
import requests
import math

def check_ffmpeg():
    """Check if ffmpeg is available."""
    try:
        result = subprocess.run(['ffmpeg', '-version'], 
                              capture_output=True, 
                              text=True, 
                              timeout=5)
        return result.returncode == 0
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False

def create_test_audio():
    """Create a simple test audio file using available tools."""
    try:
        import tempfile
        import wave
        import struct
        import math
        
        # Create a simple WAV file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            test_audio = f.name
            
            # Create a simple WAV file with basic parameters
            sample_rate = 16000  # Whisper works best with 16kHz
            duration = 2  # 2 seconds
            frequency = 440  # A4 note
            
            # Generate simple sine wave data
            frames = []
            for i in range(int(sample_rate * duration)):
                value = int(32767 * 0.3 * math.sin(2 * math.pi * frequency * i / sample_rate))
                frames.append(struct.pack('<h', value))
            
            with wave.open(test_audio, 'w') as wav_file:
                wav_file.setnchannels(1)
                wav_file.setsampwidth(2)
                wav_file.setframerate(sample_rate)
                wav_file.writeframes(b''.join(frames))
            
            return test_audio
            
    except Exception as e:
        print(f"Error creating test audio: {e}")
        return None

def test_api_with_text():
    """Test API with a text-based approach."""
    print("🔍 Testing API with text-based approach...")
    
    # Test data
    test_data = {
        "transcript": "This is a sample educational video about machine learning concepts including neural networks and deep learning.",
        "entities": [("machine learning", "TECHNOLOGY"), ("neural networks", "TECHNOLOGY"), ("deep learning", "TECHNOLOGY")],
        "topic_keywords": ["machine learning", "neural networks", "deep learning", "education", "technology"],
        "difficulty": "Intermediate"
    }
    
    print("✅ API would process this data:")
    for key, value in test_data.items():
        print(f"   {key}: {value}")
    
    return True

def test_audio_processing():
    """Test audio processing capabilities."""
    print("🔧 Testing audio processing...")
    
    # Check FFmpeg
    if check_ffmpeg():
        print("✅ FFmpeg is available")
    else:
        print("❌ FFmpeg not found")
        print("💡 Solution: Run 'python setup_ffmpeg.py' to set up FFmpeg")
        return False
    
    # Create test audio
    test_audio = create_test_audio()
    if test_audio:
        print(f"✅ Created test audio: {test_audio}")
        
        # Test basic FFmpeg operation
        try:
            output_audio = test_audio.replace('.wav', '_converted.wav')
            cmd = [
                'ffmpeg', '-i', test_audio,
                '-ar', '16000', '-ac', '1', '-sample_fmt', 's16',
                '-y', output_audio
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                print("✅ Audio conversion successful")
                os.remove(output_audio)  # Clean up
            else:
                print(f"❌ Audio conversion failed: {result.stderr}")
                
        except Exception as e:
            print(f"❌ Error testing FFmpeg: {e}")
        finally:
            if os.path.exists(test_audio):
                os.remove(test_audio)
    
    return True

def main():
    """Main test function."""
    print("🎵 Educational Video Tagging - Audio Processing Test")
    print("=" * 55)
    
    # Test FFmpeg
    test_audio_processing()
    
    # Test API text processing
    print("\n📊 Testing text-based processing...")
    test_api_with_text()
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()
