#!/bin/bash

# Personal Finance Web App Startup Script
echo "🚀 Starting Personal Finance Web Application..."
echo "================================================"

# Check if we're in the right directory
if [ ! -f "examples/finance_web_app.py" ]; then
    echo "❌ Error: Please run this script from the agenticai directory"
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

# Check if Flask is installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📦 Installing Flask..."
    pip install flask
fi

# Start the web application
echo "🌐 Starting web server..."
echo "📍 Access your finance tracker at: http://localhost:5000"
echo "🔍 Features available:"
echo "   • Dashboard with budget alerts"
echo "   • Transaction management"  
echo "   • Budget monitoring"
echo "   • Financial reports with charts"
echo ""
echo "💡 Tip: Use Ctrl+C to stop the server"
echo "================================================"

cd examples && python finance_web_app.py
