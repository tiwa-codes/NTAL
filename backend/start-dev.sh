#!/bin/bash

# NTAL Backend Development Server Script

echo "🏥 Starting NTAL Telehealth Backend..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚙️  Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/upgrade dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Seed database if it doesn't exist
if [ ! -f "ntal.db" ]; then
    echo "🌱 Seeding database..."
    python seed_data.py
fi

# Start server
echo ""
echo "🚀 Starting FastAPI server..."
echo "📚 API Documentation: http://localhost:8000/api/docs"
echo "❤️  Health Check: http://localhost:8000/api/v1/health"
echo ""

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
