# AI Fashion Stylist Assistant

An AI-powered personal fashion stylist that provides personalized style recommendations based on user images, preferences, and occasion requirements.

## Features

- **Image Analysis**: Upload your photos to extract body shape, skin tone, and style attributes
- **Style Profiling**: Create and manage style profiles with your preferences
- **Personalized Recommendations**: Get outfit recommendations tailored to your body type and style preferences
- **Product Discovery**: Find matching products from online retailers within your budget
- **Virtual Lookbook**: Save and organize your favorite outfit recommendations

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **AI/ML**: OpenAI GPT-4o Vision, Vector Embeddings, Weaviate
- **Data Storage**: SQLite (development), PostgreSQL (production)
- **Authentication**: JWT based authentication

## Getting Started

### Prerequisites

- Python 3.9+
- Virtual Environment
- OpenAI API Key

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd ai-fashion-shopper
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file based on `.env.example` and fill in your API keys:

```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

5. Create the database:

```bash
python -m app.create_db
```

### Running the Application

Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000, and the API documentation at http://localhost:8000/docs.

## API Documentation

The API documentation is automatically generated and available at `/docs` when the application is running.

The main API endpoints include:

- `/api/users`: User management
- `/api/profiles`: Style profile management
- `/api/images`: Image upload and analysis
- `/api/recommendations`: Style recommendations

## Development

### Project Structure

```
app/
  ├── main.py              # Application entry point
  ├── config.py            # Configuration settings
  ├── database.py          # Database connection
  ├── models/              # SQLAlchemy models
  ├── schemas/             # Pydantic schemas
  ├── routers/             # API route handlers
  ├── dependencies/        # Dependency injection
  ├── services/            # Business logic
  └── tests/               # Unit and integration tests
```

### Running Tests

```bash
pytest
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the vision and language models
- FastAPI for the web framework
- Weaviate for vector search capabilities 