#!/bin/bash
# Script to run the direct recommendation test

# Ensure the script exits on any error
set -e

echo "🧠 Running direct recommendation test with OpenAI API..."

# Activate virtual environment
source venv/bin/activate

# Check if OpenAI package is installed, install if not
if ! pip list | grep -q "openai"; then
    echo "Installing required packages..."
    pip install openai
fi

# Make the Python script executable if it's not already
chmod +x direct_recommendation_test.py

# Run the test script with any provided arguments
echo "Running direct_recommendation_test.py..."
python direct_recommendation_test.py "$@"

echo "✅ Test completed!" 