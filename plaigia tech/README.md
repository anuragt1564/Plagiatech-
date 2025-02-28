# PlagiaTech Backend

Backend API for PlagiaTech, a plagiarism checker and text rephrasing tool.

## Features

- **Plagiarism Checking**: Detect plagiarism in text using external API integration
- **Text Rephrasing**: AI-powered text rephrasing to create unique content
- **User Management**: Registration, authentication, and premium subscriptions
- **Asynchronous Processing**: Background task processing for long-running operations
- **Rate Limiting**: Prevent abuse with configurable rate limits
- **Caching**: Improve performance with result caching

## Tech Stack

- **Framework**: FastAPI
- **Async Processing**: Celery with Redis
- **Authentication**: JWT-based token authentication
- **API Integration**: 
  - Plagiarism: Copyleaks API (simulated)
  - Rephrasing: OpenAI API (simulated)

## API Endpoints

### Plagiarism

- `POST /api/check-plagiarism`: Check text for plagiarism
- `GET /api/check-plagiarism/{task_id}`: Get result of async plagiarism check

### Rephrasing

- `POST /api/rephrase`: Rephrase text using AI
- `GET /api/rephrase/{task_id}`: Get result of async rephrasing task

### User Management

- `POST /api/register`: Register a new user
- `POST /api/token`: Get access token (login)
- `GET /api/me`: Get current user information
- `GET /api/usage`: Get usage statistics
- `POST /api/premium`: Upgrade to premium
- `GET /api/history`: Get user's history

## Setup

### Quick Start

The easiest way to run the application is using the provided run script:

```
./run.sh
```

This script will:
1. Check for required dependencies
2. Create a default `.env` file if one doesn't exist
3. Install Python dependencies if needed
4. Start Redis server if not already running
5. Start Celery worker
6. Start FastAPI server
7. Start frontend server
8. Open the frontend in your browser

All services will run in the background with logs saved to files. Press Ctrl+C to stop all services.

### Manual Setup

If you prefer to run each component separately:

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables in `.env` file
4. Start Redis server:
   ```
   redis-server
   ```
5. Start Celery worker:
   ```
   celery -A celery_worker worker --loglevel=info
   ```
6. Run the backend API:
   ```
   uvicorn main:app --reload
   ```
7. Serve the frontend (in a separate terminal):
   ```
   python serve_frontend.py
   ```
   This will open a browser window with the frontend at http://localhost:3000

### Docker Setup

Alternatively, you can use Docker Compose to run the entire stack:

```
docker-compose up
```

This will start the following services:
- Web server (FastAPI backend) at http://localhost:8000
- Celery worker for background tasks
- Redis for message broker and caching

To serve the frontend with Docker running, use:
```
python serve_frontend.py
```

## Environment Variables

Create a `.env` file with the following variables:

```
# API Keys
COPYLEAKS_API_KEY=your_copyleaks_api_key
OPENAI_API_KEY=your_openai_api_key

# JWT Settings
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Redis Settings
REDIS_URL=redis://localhost:6379/0

# Server Settings
PORT=8000
DEBUG=True
ENVIRONMENT=development

# Rate Limiting
RATE_LIMIT_DEFAULT=100/hour
RATE_LIMIT_FREE_TIER=10/day
```

## API Documentation

When the server is running, you can access the API documentation at:

- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc

## Frontend Integration

The frontend sends user-input text via POST requests to the API endpoints and expects JSON responses. The backend is designed to work seamlessly with the provided frontend.

## Deployment

For production deployment:

1. Set `ENVIRONMENT=production` in `.env`
2. Ensure all API keys are properly configured
3. Set a strong `JWT_SECRET_KEY`
4. Deploy using a production ASGI server like Gunicorn with Uvicorn workers:
   ```
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app
   ```

## Testing

You can test the API endpoints using the included test script:

```
./test_api.py
```

Options:
- `--url`: API base URL (default: http://localhost:8000/api)
- `--text`: Text to use for testing
- `--register`: Test user registration
- `--username`: Username for testing
- `--email`: Email for testing
- `--password`: Password for testing

Example:
```
./test_api.py --register --username=testuser --email=test@example.com
```

## Future Improvements

- Database integration for user management and history
- WebSockets for real-time task status updates
- More sophisticated rate limiting based on user tiers
- Enhanced error handling and logging
- Comprehensive test suite
