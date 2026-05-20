Write-Host "🍎 Calorie Counter App Launcher" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = & C:/Python313/python.exe --version 2>&1
    Write-Host "✅ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found! Please install Python first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Streamlit is installed
try {
    $streamlitVersion = & C:/Python313/python.exe -c "import streamlit; print(streamlit.__version__)" 2>&1
    Write-Host "✅ Streamlit found: $streamlitVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Streamlit not found! Installing packages..." -ForegroundColor Yellow
    & C:/Python313/python.exe -m pip install -r requirements.txt
}

Write-Host ""
Write-Host "🚀 Starting Calorie Counter App..." -ForegroundColor Cyan
Write-Host "The app will open in your default browser at: http://localhost:8501" -ForegroundColor Yellow
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""

# Start the Streamlit app
& C:/Python313/python.exe -m streamlit run calorie_counter.py