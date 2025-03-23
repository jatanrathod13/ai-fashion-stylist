# Fashion Recommendation Test Scripts

This directory contains test scripts for the AI Fashion Shopper application, with a focus on testing the recommendation functionality with the OpenAI API.

## Available Scripts

### 1. Basic Server Test
- **Script**: `simple_test.py`
- **Purpose**: Tests basic server connectivity and API endpoints
- **Usage**:
  ```
  python simple_test.py
  ```

### 2. Full API Recommendation Test
- **Script**: `test_recommendation.py`
- **Purpose**: Tests the complete recommendation flow through the application's API, including authentication and recommendation generation
- **Usage**:
  ```
  python test_recommendation.py
  ```
- **Options**:
  - `--api-url`: API base URL (default: http://localhost:8000)
  - `--email`: User email for authentication
  - `--password`: User password
  - `--profile-id`: Style profile ID to use

### 3. Direct OpenAI API Test
- **Script**: `test_openai_direct.py`
- **Purpose**: Tests the OpenAI API directly for fashion recommendations, bypassing the application's API
- **Usage**:
  ```
  ./test_openai_direct.py [options]
  ```
- **Options**:
  - `--model`: OpenAI model to use (default: gpt-4o-mini)
  - `--occasion`: Occasion for the outfit (default: casual weekend)
  - `--season`: Season for the outfit (default: summer)
  - `--budget`: Budget range in format 'min-max' (e.g., '100-400')
  - `--budget-min`: Minimum budget in USD (default: 100.0)
  - `--budget-max`: Maximum budget in USD (default: 400.0)
  - `--body-shape`: Body shape (default: Rectangle)
  - `--skin-tone`: Skin tone (default: Medium)
  - `--height`: Height in cm (default: 175)
  - `--style-preferences`: Comma-separated style preferences (default: casual,minimalist,classic)
  - `--favorite-colors`: Comma-separated favorite colors (default: blue,gray,white)
  - `--disliked-items`: Comma-separated disliked items (default: crop tops,skinny jeans)
  - `--special-requirements`: Special requirements or notes

### 4. Shell Scripts

#### Run Tests
- **Script**: `run_tests.sh`
- **Purpose**: Comprehensive test runner that checks if the server is running, runs the simple test, and then runs the full recommendation test
- **Usage**:
  ```
  ./run_tests.sh
  ```

#### Run Direct Test
- **Script**: `run_direct_test.sh`
- **Purpose**: Runner for the direct OpenAI API test with a simpler command interface
- **Usage**:
  ```
  ./run_direct_test.sh [options]
  ```
- **Example Usage**:
  ```
  ./run_direct_test.sh --model "gpt-4o-mini" --occasion "formal dinner" --season "fall" --budget "150-500"
  ./run_direct_test.sh --occasion "beach vacation" --season "summer" --special-requirements "waterproof"
  ```

## Setup

1. Make sure the scripts are executable:
   ```
   chmod +x run_tests.sh run_direct_test.sh test_openai_direct.py
   ```

2. Set up the OpenAI API key in one of two ways:
   - Create a `.env` file with `OPENAI_API_KEY=your_api_key`
   - Set the environment variable: `export OPENAI_API_KEY=your_api_key`

3. Ensure the virtual environment is activated before running scripts:
   ```
   source venv/bin/activate
   ```

## Test User Account

For the full API tests, a test user has been set up with the following credentials:
- **Email**: testuser123@example.com
- **Password**: testpassword123
- **Profile ID**: 3

## Integration Plan

See the `integration_plan.md` file for a detailed plan on how to integrate the successful direct test functionality into the main application. 