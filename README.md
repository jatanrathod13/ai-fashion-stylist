# AI Fashion Stylist 👔👗👟

AI-powered personal fashion stylist that provides personalized style recommendations based on user images, preferences, and occasion requirements.

## Project Status

This project is currently under active development. The foundational architecture and key features are in place, and we're continuously enhancing its capabilities.

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
   source venv/bin/activate  # On Windows: venv\Scriptsctivate
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
   python -m app.create_db
   ```

6. Run the application:
   ```
   python run.py
   ```

The API will be available at http://localhost:8000, and the API documentation can be accessed at http://localhost:8000/docs.
Always check that you are in virtual environment before running the application. 
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

## Database Management

The AI Fashion Shopper uses SQLAlchemy with Alembic for database management and migrations. The application supports both SQLite (development) and PostgreSQL (production) databases.

### Database Setup

1. Configure your database URL in `.env`:
   ```
   # For SQLite (development)
   DATABASE_URL=sqlite+aiosqlite:///./fashion_stylist.db
   
   # For PostgreSQL (production)
   # DATABASE_URL=postgresql+asyncpg://username:password@localhost:5432/ai_fashion_shopper
   ```

2. Initialize the database with Alembic migrations:
   ```
   python -m app.create_db
   ```

### Managing Database Migrations

When making changes to database models:

1. Create a new migration:
   ```
   alembic revision --autogenerate -m "Description of changes"
   ```

2. Apply the migration:
   ```
   alembic upgrade head
   ```

3. Rollback to a previous version if needed:
   ```
   alembic downgrade -1
   ```

### Migration Helper Tool

For transitioning from existing databases or managing complex migration scenarios, a migration helper tool is available:

```
# Mark existing migrations as applied (for existing databases)
python -m app.db_migration_helper --mark-applied

# Reset the database and apply migrations from scratch
python -m app.db_migration_helper --reset

# Run migrations without resetting
python -m app.db_migration_helper --run-migrations
```

## Database Architecture

The application uses an async SQLAlchemy ORM with the following key components:

- **Base Model**: Defined in `app/models/base.py`, provides common functionality for all models
- **User Model**: Stores user authentication and profile data
- **StyleProfile**: Stores user style preferences and characteristics
- **Recommendation**: Stores AI-generated fashion recommendations
- **Outfit**: A complete outfit recommendation with multiple components
- **OutfitComponent**: Individual pieces that make up an outfit
- **Product**: E-commerce product information for recommendations

The architecture supports both SQLite for development and PostgreSQL for production deployments.

### Database Schema

```
users ┬── style_profiles ┬── feedback_history
      │                  └── images
      └── recommendations ┬── outfits ┬── outfit_components ┬── products
                          │           └── clothing_items    │
                          └── feedback_history              │
                                                          └── ...
```
