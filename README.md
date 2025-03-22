# AI Fashion Stylist 👔👗👟

An AI-powered personal fashion stylist that provides personalized style recommendations based on user images, preferences, and occasion requirements.

## Project Status

This project is currently under active development. The foundational architecture and key features are in place, and we're continuously enhancing its capabilities.

## Features

- **User Management**: JWT-based authentication system
- **Image Analysis**: Upload your photos to extract body shape, skin tone, and style attributes
- **Style Profiling**: Create and manage style profiles with your preferences
- **Personalized Recommendations**: Get outfit recommendations tailored to your body type and style preferences
- **Product Discovery**: Find matching products from online retailers within your budget
- **Virtual Lookbook**: Save and organize your favorite outfit recommendations
- **Similarity Search**: Find style profiles with similar characteristics

## Technology Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic
- **AI/ML**: OpenAI GPT-4o Vision, Vector Embeddings
- **Database**: SQLite (development), PostgreSQL (production)
- **Authentication**: JWT (JSON Web Tokens)
- **Testing**: Pytest

## Getting Started

### Prerequisites

- Python 3.10+
- OpenAI API Key
- Weaviate instance (for vector search)

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jatanrathod13/ai-fashion-stylist.git
   cd ai-fashion-stylist
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

5. Initialize the database:
   ```bash
   python -m app.create_db
   ```

6. Run the application:
   ```bash
   python run.py
   ```

The API will be available at http://localhost:8000, and the API documentation can be accessed at http://localhost:8000/docs.

## API Documentation

The API documentation is automatically generated and available at `/docs` when the application is running.

The main API endpoints include:

- `/api/users`: User management
- `/api/auth`: Authentication and token generation
- `/api/profiles`: Style profile management
- `/api/images`: Image upload and analysis
- `/api/recommendations`: Fashion recommendations

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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI for providing the vision and language models
- FastAPI for the web framework
- Weaviate for vector search capabilities
