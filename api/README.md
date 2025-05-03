# Finexia API

This directory contains the API framework for the Finexia stock market prediction system. The API is built with FastAPI, a modern, high-performance web framework for building APIs with Python.

## Architecture

The API follows a clean, layered architecture:

- **Routers**: Handle HTTP requests and define endpoints
- **Services**: Contain business logic
- **Models**: Define data structures for request/response validation
- **Dependencies**: Provide reusable components like auth and database access
- **Middleware**: Process requests/responses for cross-cutting concerns

## Directory Structure

```
api/
├── __init__.py
├── main.py                   # Main FastAPI application entry point
├── config.py                 # API configuration settings
├── middleware/               # Custom middleware components
│   ├── __init__.py
│   ├── auth.py               # Authentication middleware
│   ├── rate_limiter.py       # Rate limiting middleware
│   └── logging.py            # Request logging middleware
├── routers/                  # Route modules for different API sections
│   ├── __init__.py
│   ├── predictions.py        # Prediction endpoints
│   ├── historical.py         # Historical data endpoints
│   ├── models.py             # Model management endpoints
│   └── system.py             # System management endpoints
├── models/                   # Pydantic data models
│   ├── __init__.py
│   ├── prediction.py         # Prediction data models
│   ├── historical.py         # Historical data models
│   ├── model.py              # Model status and config models
│   └── system.py             # System status models
├── services/                 # Business logic layer
│   ├── __init__.py
│   ├── prediction_service.py # Prediction business logic
│   ├── historical_service.py # Historical data business logic
│   ├── model_service.py      # Model management business logic
│   └── system_service.py     # System management business logic
├── dependencies/             # FastAPI dependencies
│   ├── __init__.py
│   ├── db.py                 # Database session dependency
│   └── auth.py               # Authentication dependencies
└── utils/                    # Utility functions
    ├── __init__.py
    ├── response.py           # Response formatting utilities
    └── validation.py         # Input validation utilities
```

## API Endpoints

The API is organized into several logical sections:

### Predictions

- `GET /api/v1/predictions/{symbol}` - Get latest prediction for a symbol
- `GET /api/v1/predictions/` - List predictions with various filters
- `POST /api/v1/predictions/refresh/{symbol}` - Force refresh a prediction

### Historical Data

- `GET /api/v1/historical/eod/{symbol}` - Get historical EOD data
- `GET /api/v1/historical/features/{symbol}` - Get feature data

### Models

- `GET /api/v1/models/{symbol}` - Get model status and metrics
- `GET /api/v1/models/` - List all models
- `POST /api/v1/models/train/{symbol}` - Train a model
- `GET /api/v1/models/performance` - Get performance metrics
- `GET /api/v1/models/{symbol}/history` - Get performance history

### System

- `GET /api/v1/system/status` - Get system status
- `POST /api/v1/system/run-pipeline` - Trigger daily pipeline

## Authentication

The API uses JWT (JSON Web Token) authentication. To access protected endpoints:

1. Obtain a token via `POST /api/v1/auth/token`
2. Include the token in the Authorization header:
   `Authorization: Bearer <token>`

## Running the API

```bash
# Install dependencies
pip install -r requirements.txt

# Run the API with auto-reload for development
uvicorn api.main:app --reload

# Run for production
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## API Documentation

When the API is running, you can access:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Configuration

The API can be configured via environment variables or a `.env` file. See `api/config.py` for available settings.

## Error Handling

The API uses standard HTTP status codes for errors:

- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server-side error

## Scaling

The API is designed to be horizontally scalable:

- Stateless authentication with JWT
- Optimized database access with connection pooling
- Background task processing for intensive operations
- Rate limiting to prevent abuse
- Efficient data serialization and validation