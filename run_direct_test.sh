#!/bin/bash
# Script to run the direct OpenAI API test for fashion recommendations

# Activate virtual environment
source venv/bin/activate

echo "🧠 Running direct OpenAI API test for fashion recommendations..."

# Check if any arguments were provided
if [ "$#" -eq 0 ]; then
    echo "No arguments provided. Using default parameters."
    echo "Example usage:"
    echo "  $0 --model \"gpt-4o-mini\" --occasion \"formal dinner\" --season \"fall\" --budget \"150-500\""
    echo "  $0 --occasion \"beach vacation\" --season \"summer\" --special-requirements \"waterproof\""
    echo ""
fi

# Run the test with provided parameters
./test_openai_direct.py "$@"

echo "✅ Test completed!" 