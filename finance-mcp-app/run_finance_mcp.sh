#!/bin/bash

# Finance MCP Web App Startup Script
# This script starts both the MCP server and the web application

echo "🏦 Starting Finance MCP Application..."
echo "==============================================="

# Check if virtual environment exists
if [ ! -d "../.venv" ]; then
    echo "❌ Virtual environment not found. Please run this from the finance-mcp-app directory."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../.venv/bin/activate

# Check if required packages are installed
echo "📦 Checking dependencies..."
python -c "import fastmcp, langchain_ollama, flask" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Missing required packages. Installing..."
    pip install fastmcp langchain-ollama flask
fi

# Check if Ollama is running and llama3.2 is available
echo "🦙 Checking Ollama..."
ollama list | grep -q "llama3.2"
if [ $? -ne 0 ]; then
    echo "📥 Pulling Llama 3.2 model..."
    ollama pull llama3.2
fi

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down application..."
    echo "👋 Goodbye!"
    exit 0
}

# Set up signal handlers for graceful shutdown
trap cleanup SIGINT SIGTERM

# Start Web Application (which includes MCP client)
echo "🌐 Starting Finance Web App with integrated MCP..."
echo "📡 Web app will be available at: http://localhost:5000"
echo "🤖 AI Assistant powered by Ollama Llama 3.2"
echo "💡 The web app creates its own MCP client connection"
echo ""
echo "Press Ctrl+C to stop the application"
echo "==============================================="

# Start web app (it handles its own MCP client)
python finance_web_mcp.py
