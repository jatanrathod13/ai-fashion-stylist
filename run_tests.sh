#!/bin/bash
# Script to run the recommendation tests

# Activate virtual environment
source venv/bin/activate

# Check if the server is already running
if pgrep -f "python run.py" > /dev/null; then
    echo "🔍 Server is already running..."
else
    echo "🚀 Starting the server..."
    # Start the server in the background
    python run.py &
    # Save the process ID
    SERVER_PID=$!
    echo "⏳ Waiting for server to initialize..."
    sleep 5
fi

# Run the simple test to check if the server is accessible
echo "🔍 Running simple server test..."
python simple_test.py --wait 2

# Check if the simple test was successful
if [ $? -ne 0 ]; then
    echo "❌ Simple test failed. Please check the server logs for errors."
    # Cleanup if we started the server
    if [ -n "$SERVER_PID" ]; then
        echo "🛑 Stopping the server (PID: $SERVER_PID)..."
        kill $SERVER_PID
    fi
    exit 1
fi

# Run the full recommendation test
echo -e "\n🧪 Running full recommendation test..."
python test_recommendation.py

# Check if the recommendation test was successful
TEST_RESULT=$?

# Cleanup if we started the server
if [ -n "$SERVER_PID" ]; then
    echo "🛑 Stopping the server (PID: $SERVER_PID)..."
    kill $SERVER_PID
fi

# Provide feedback based on the test result
if [ $TEST_RESULT -eq 0 ]; then
    echo "✅ All tests completed successfully!"
else
    echo "❌ Recommendation test failed. Please check the server logs for errors."
fi

exit $TEST_RESULT 