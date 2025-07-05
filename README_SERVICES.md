# Domain-Separated FastAPI Services

This project has been refactored to run HR and IT domains as separate FastAPI services on different ports for better scalability and isolation.

## Architecture Overview

- **HR Service**: Runs on port 8001
- **IT Service**: Runs on port 8002
- **Redis**: Used for caching (optional)
- **Sentry**: Used for error reporting (optional)

## Features

### Performance Optimizations
- Redis caching for non-streaming endpoints
- GZip compression for responses
- Parallel processing for similarity calculations
- Request timing headers
- Connection pooling
- Async operations throughout

### Error Reporting
- Structured logging to files and console
- Sentry integration for production error tracking
- Request ID tracking
- Performance monitoring
- Automatic error context capture

### Common Functionality
Both services share:
- Chat endpoints
- Query processing
- Summarization
- Translation
- Similarity calculations
- Personal knowledge base
- Token counting
- Records management

### Domain-Specific Features
Each service can have its own domain-specific endpoints:
- HR: `/hr/info`, `/hr/systems`
- IT: `/it/info`, `/it/systems`, `/it/status`

## Running the Services

### Option 1: Run Both Services Together
```bash
python start_all_services.py
```

### Option 2: Run Services Separately
```bash
# Terminal 1 - HR Service
python start_hr_service.py

# Terminal 2 - IT Service
python start_it_service.py
```

### Option 3: Using Docker Compose (Recommended)
```bash
# Copy environment file
cp .env.example .env

# Edit .env with your configuration
# Then start all services
docker-compose up -d

# View logs
docker-compose logs -f hr_service
docker-compose logs -f it_service

# Stop services
docker-compose down
```

## Configuration

### Environment Variables
Create a `.env` file based on `.env.example`:

```env
# Service ports
HR_SERVICE_PORT=8001
IT_SERVICE_PORT=8002

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379

# Sentry (optional)
SENTRY_DSN=your-sentry-dsn

# Environment
ENVIRONMENT=production
```

### Domain Configuration
Each domain's configuration is in:
- `domains/hr/config.py`
- `domains/it/config.py`

## API Endpoints

### Common Endpoints (available on both services)
- `GET /health` - Health check
- `GET /domain-info` - Domain information
- `POST /chat` - Chat with AI
- `POST /query` - Process queries
- `POST /summarize` - Summarize text
- `POST /translate` - Translate text
- `POST /similarity` - Calculate text similarity
- `POST /prompt_fill` - Fill prompts
- `POST /count-tokens` - Count tokens
- `POST /get_records` - Get process records
- `GET /test_error` - Test error handling

### HR-Specific Endpoints (port 8001)
- `GET /hr/info` - HR service information
- `GET /hr/systems` - HR systems information

### IT-Specific Endpoints (port 8002)
- `GET /it/info` - IT service information
- `GET /it/systems` - IT systems information
- `GET /it/status` - IT systems status

## Monitoring

### Logs
- Service logs: `service_YYYYMMDD.log`
- Docker logs: `logs/hr/` and `logs/it/`

### Performance Metrics
- Check `X-Process-Time` header in responses
- Monitor Redis cache hit rates
- Review Sentry performance data

### Error Tracking
- Local: Check log files
- Production: Use Sentry dashboard

## Development

### Adding New Domain-Specific Features
1. Add routes in `services/hr/hr_service.py` or `services/it/it_service.py`
2. Override `_add_routes()` method
3. Call `super()._add_routes()` first to include common routes

### Adding Common Features
1. Update `services/common/base_service.py`
2. All services will automatically inherit the changes

## Troubleshooting

### Redis Connection Failed
- Service will run without caching
- Check Redis connection settings
- Ensure Redis is running

### Port Already in Use
- Change ports in environment variables
- Check for existing processes

### Import Errors
- Ensure all requirements are installed: `pip install -r requirements.txt`
- Check Python path configuration

## Production Deployment

1. Set `ENVIRONMENT=production` in `.env`
2. Configure Sentry DSN for error tracking
3. Use Docker Compose for deployment
4. Set up proper logging rotation
5. Configure reverse proxy (nginx) if needed
6. Monitor service health endpoints