# AI Fashion Stylist

AI-powered personal fashion stylist that provides personalized style recommendations based on user images, preferences, and occasion requirements.

## Features

- User management with JWT authentication
- Style profile creation and management
- Image upload and analysis using OpenAI's Vision API
- Personalized fashion recommendations based on user's body attributes and style preferences
- Similarity search for finding style profiles with similar characteristics

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **AI**: OpenAI GPT-4o Vision API, Vector embeddings
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: JWT (JSON Web Tokens)
- **Testing**: Pytest

## Getting Started

### Prerequisites

- Python 3.10+
- OpenAI API key
- Weaviate instance (for vector search)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/jatanrathod13/ai-fashion-stylist.git
   cd ai-fashion-stylist
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\\Scripts\\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   ```
   cp .env.example .env
   # Edit .env with your credentials
   ```

5. Initialize the database:
   ```
   python -m app.core.db
   ```

6. Run the application:
   ```
   python run.py
   ```

The API will be available at http://localhost:8000, and the API documentation can be accessed at http://localhost:8000/docs.

## API Documentation

The API provides the following endpoints:

- `/api/users`: User management
- `/api/auth`: Authentication and token generation
- `/api/profiles`: Style profile management
- `/api/images`: Image upload and analysis
- `/api/recommendations`: Fashion recommendations

For detailed API documentation, visit the `/docs` endpoint after starting the application.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.