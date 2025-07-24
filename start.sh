#!/bin/bash

# FairClaimRCM Quick Start Script
# This script helps you get FairClaimRCM running quickly

set -e  # Exit on any error

echo "🏥 FairClaimRCM Quick Start"
echo "=========================="

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "   Please install Python 3.8 or higher and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Are you in the FairClaimRCM directory?"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating environment configuration..."
    cp .env.example .env
    echo "✅ Created .env file (you may want to customize it)"
else
    echo "✅ Environment configuration already exists"
fi

# Run basic tests
echo "🧪 Running basic tests..."
python tests/test_core.py

# Start the API server
echo ""
echo "🚀 Starting FairClaimRCM API server..."
echo "   API will be available at: http://localhost:8000"
echo "   Documentation at: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd api
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
