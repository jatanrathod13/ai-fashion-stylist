#!/bin/bash
# Script to test the recommendation endpoint with proper authentication

# Ensure the script exits on any error
set -e

echo "🧪 Testing recommendation endpoint with authentication..."

# Activate virtual environment
source venv/bin/activate

# Check if httpx is installed, install if not
if ! pip list | grep -q "httpx"; then
    echo "Installing required packages..."
    pip install httpx
fi

# Make the Python script executable if it's not already
chmod +x test_recommendation_endpoint.py

# Check if the server is running
echo "Checking if the server is running..."
# Try to access the root endpoint to see if server is up
if ! curl -s http://localhost:8000/ > /dev/null; then
    echo "❌ Server is not running. Please start it with: python run.py"
    exit 1
fi

echo "✅ Server is running."

# Run the test script
echo "Running test_recommendation_endpoint.py..."
python test_recommendation_endpoint.py "$@"

echo "✅ Test completed!" 