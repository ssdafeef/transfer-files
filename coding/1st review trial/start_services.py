"""
IDS System Startup Script
Starts all required services for the AI-Driven Intrusion Detection System
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_service(command, name, wait_time=2):
    """Start a service in a new process"""
    print(f"🚀 Starting {name}...")
    try:
        if sys.platform == "win32":
            # For Windows, start in new command prompt window
            process = subprocess.Popen(
                ["cmd", "/c", "start", "cmd", "/k", command],
                cwd=Path.cwd(),
                shell=False
            )
        else:
            # For Unix-like systems
            process = subprocess.Popen(
                command.split(),
                cwd=Path.cwd()
            )
        
        time.sleep(wait_time)
        print(f"✅ {name} started successfully")
        return process
    except Exception as e:
        print(f"❌ Failed to start {name}: {e}")
        return None

def main():
    """Main startup function"""
    print("🛡️  AI-Driven Intrusion Detection System - Startup Script")
    print("=" * 60)
    
    # Get Python executable path
    python_exe = "C:/Python313/python.exe"
    
    print("Starting services in order...")
    print()
    
    # 1. Start API server
    api_command = f"{python_exe} api.py"
    start_service(api_command, "API Server", 3)
    
    # 2. Start main IDS processor (optional - can be started manually)
    print("📝 Note: You can start the main IDS processor manually with:")
    print(f"   {python_exe} main.py --file data/sample_traffic.txt")
    print()
    
    # 3. Start Streamlit dashboard
    streamlit_command = f"{python_exe} -m streamlit run streamlit_app.py"
    start_service(streamlit_command, "Streamlit Dashboard", 5)
    
    print()
    print("🎉 All services started!")
    print()
    print("📋 Quick Access URLs:")
    print("   • Streamlit Dashboard: http://localhost:8501")
    print("   • API Server: http://localhost:5000")
    print("   • API Health Check: http://localhost:5000/health")
    print()
    print("🔧 Manual Commands:")
    print(f"   • Run IDS Processor: {python_exe} main.py")
    print(f"   • Test API: {python_exe} test_api_integration.py")
    print(f"   • Performance Test: {python_exe} performance_comparison.py")
    print()
    print("⚠️  Make sure to keep this terminal open to see the services running.")
    
    # Keep the script running
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("\n🛑 Shutdown requested by user")
        print("Services will continue running in their separate windows.")

if __name__ == "__main__":
    main()