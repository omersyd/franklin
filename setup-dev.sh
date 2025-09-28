#!/bin/bash

# Franklin Search - Development Setup Script
# This script sets up the complete development environment

echo "🚀 Franklin Search - Development Setup"
echo "======================================"

# Check if we're in a Docker environment or local development
if [ -f /.dockerenv ]; then
    echo "📦 Docker environment detected"
    PYTHON_CMD="python"
else
    echo "💻 Local development environment detected"
    # Try to detect Python command
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        echo "❌ Python not found. Please install Python 3.8 or higher."
        exit 1
    fi
fi

echo "🔧 Using Python command: $PYTHON_CMD"

# Run database migrations
echo ""
echo "1️⃣  Running database migrations..."
$PYTHON_CMD manage.py migrate

if [ $? -ne 0 ]; then
    echo "❌ Database migrations failed"
    exit 1
fi

# Load initial data
echo ""
echo "2️⃣  Loading initial data (apps and reviews)..."
$PYTHON_CMD manage.py load_initial_data

if [ $? -ne 0 ]; then
    echo "⚠️  Initial data loading failed (you may need to run this manually later)"
fi

# Create seed users
echo ""
echo "3️⃣  Creating test users..."
$PYTHON_CMD manage.py seed_users

if [ $? -ne 0 ]; then
    echo "⚠️  Seed users creation failed"
fi

echo ""
echo "✅ Development setup completed successfully!"
echo ""
echo "📝 Test Login Credentials:"
echo "   Regular User:  testuser / testpass123"
echo "   Supervisor:    supervisor / supervisor123"
echo ""

# Show next steps based on environment
if [ -f /.dockerenv ]; then
    echo "🌐 Your application should be running at: http://localhost:8000"
else
    echo "🚀 Next steps:"
    echo "   1. Start the development server:"
    echo "      $PYTHON_CMD manage.py runserver"
    echo ""
    echo "   2. Open your browser and go to:"
    echo "      http://localhost:8000"
fi

echo ""
echo "📚 Additional Commands:"
echo "   - Reset test users:     $PYTHON_CMD manage.py seed_users --reset"
echo "   - Create superuser:     $PYTHON_CMD manage.py createsuperuser"
echo "   - Check status page:    http://localhost:8000/status"
echo ""
echo "🎉 Happy coding!"