#!/bin/bash

# Personal # Start the web application
echo "🌐 Starting web server..."
echo "📍 Access your finance tracker at: http://localhost:5001"
echo "🔍 Features available:"
echo "   • Dashboard with budget alerts"
echo "   • Transaction management"  
echo "   • Budget monitoring"
echo "   • Financial reports with charts"
echo ""
echo "💡 Tip: Use Ctrl+C to stop the server"
echo "================================================"

python finance_web_app.pypp Startup Script
echo "🚀 Starting Personal Finance Web Application..."
echo "================================================"

# Check if we're in the right directory
if [ ! -f "finance_web_app.py" ]; then
    echo "❌ Error: Please run this script from the finance-mcp-app directory"
    echo "💡 Navigate to the finance-mcp-app directory first:"
    echo "   cd finance-mcp-app"
    exit 1
fi

# Activate virtual environment (from parent directory)
echo "🔧 Activating virtual environment..."
source ../.venv/bin/activate

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
