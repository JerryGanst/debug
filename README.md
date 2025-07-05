# Domain-Based Microservices Architecture

A flexible, scalable architecture for running domain-specific services with built-in RAG (Retrieval-Augmented Generation) capabilities, custom glossary management, and separated embedding services.

## 🏗️ Architecture Overview

This system provides a modular approach to deploying domain-specific services. Instead of being limited to specific domains like HR or IT, you can easily create and deploy services for any domain (Finance, Legal, Sales, Marketing, etc.).

### Key Components

1. **Domain Services**: Each domain runs as a separate FastAPI service on its own port
2. **Embedding Service**: Standalone service for text embeddings (port 8100)
3. **Redis Cache**: Optional caching layer for performance
4. **Custom Glossary**: Each domain can have its own glossary of terms
5. **Error Reporting**: Integrated Sentry support for production monitoring

## 🚀 Quick Start

### 1. Basic Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd <project-directory>

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env
```

### 2. Start a Domain Service

```bash
# Start any domain service
python start_domain_service.py <domain_name> --port <port>

# Examples:
python start_domain_service.py hr --port 8001
python start_domain_service.py finance --port 8003
python start_domain_service.py legal --port 8004

# List available domains
python start_domain_service.py --list-domains
```

### 3. Start Embedding Service

```bash
# Run the standalone embedding service
python embedding_service_api/main.py
# Runs on port 8100 by default
```

### 4. Docker Deployment

```bash
# Start all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 📁 Project Structure

```
.
├── domains/                    # Domain configurations
│   ├── hr/                    # HR domain
│   │   ├── config.py         # Domain configuration
│   │   └── templates/        # Domain-specific templates
│   ├── it/                   # IT domain
│   └── <your_domain>/        # Add new domains here
├── services/
│   ├── common/               # Shared service components
│   │   ├── base_service.py   # Base service class
│   │   ├── domain_factory.py # Dynamic domain service creation
│   │   ├── glossary_manager.py # Glossary management
│   │   ├── error_reporting.py # Error tracking
│   │   └── performance.py    # Performance optimization
│   ├── hr/                   # HR-specific service (optional)
│   └── it/                   # IT-specific service (optional)
├── embedding_service_api/     # Standalone embedding service
│   └── main.py
├── glossaries/               # Domain glossaries (auto-created)
├── routes/                   # API route handlers
├── models/                   # Data models
├── start_domain_service.py   # Generic domain starter
├── docker-compose.yml        # Docker configuration
└── requirements.txt          # Python dependencies
```

## 🔧 Adding a New Domain

### Method 1: Simple Configuration (Recommended)

1. Create a new domain directory:
```bash
mkdir -p domains/finance
```

2. Create `domains/finance/config.py`:
```python
from domains.base import BaseDomainConfig

class DomainConfig(BaseDomainConfig):
    def __init__(self):
        super().__init__()
        self.DOMAIN_NAME = "FINANCE"
        self.DOMAIN_DOC_TYPE = "Finance"
        self.custom_config = {
            "topics": "budgeting, accounting, financial planning, investments",
            "systems": "QuickBooks, SAP Finance, Excel"
        }
    
    def get_question_categories(self):
        return {
            1: "Financial calculations and procedures",
            2: "Financial policies and regulations",
            3: "General finance questions"
        }
```

3. Start the service:
```bash
python start_domain_service.py finance --port 8003
```

### Method 2: Custom Service Implementation

For domains requiring special functionality, create a custom service:

1. Create `services/finance/finance_service.py`:
```python
from services.common.base_service import BaseService

class FINANCEService(BaseService):
    def __init__(self, port: int = 8003, host: str = "0.0.0.0"):
        super().__init__(domain_name="FINANCE", port=port, host=host)
    
    def _add_routes(self):
        super()._add_routes()
        
        # Add finance-specific routes
        @self.app.get("/finance/reports")
        async def generate_reports():
            # Custom implementation
            pass
```

## 📚 API Documentation

### Common Endpoints (Available on all domain services)

#### Core Functionality
- `GET /health` - Service health check
- `GET /domain-info` - Domain configuration info
- `POST /chat` - Chat with AI assistant
- `POST /query` - Process queries with RAG
- `POST /summarize` - Summarize documents
- `POST /translate` - Translate text
- `POST /similarity` - Calculate text similarity

#### Glossary Management
- `POST /glossary/terms` - Add new term
- `GET /glossary/terms/{term}` - Get specific term
- `PUT /glossary/terms/{term}` - Update term
- `DELETE /glossary/terms/{term}` - Delete term
- `GET /glossary/search?query=...` - Search terms
- `GET /glossary/terms` - List all terms (paginated)
- `GET /glossary/categories` - List categories
- `GET /glossary/export?format=json|csv|markdown` - Export glossary
- `POST /glossary/import` - Import glossary
- `GET /glossary/stats` - Glossary statistics

#### Monitoring
- `GET /metrics` - Performance metrics
- `GET /test_error` - Test error handling

### Embedding Service Endpoints (Port 8100)

- `GET /health` - Service health check
- `POST /embeddings` - Generate embeddings
- `POST /embeddings/batch` - Batch embedding generation
- `POST /similarity` - Calculate similarity
- `GET /models` - List available models
- `GET /cache/stats` - Cache statistics
- `POST /cache/clear` - Clear cache

## 🔐 Custom Glossary Usage

Each domain can maintain its own glossary of terms and definitions:

### Adding Terms via API

```bash
# Add a term
curl -X POST http://localhost:8001/glossary/terms \
  -H "Content-Type: application/json" \
  -d '{
    "term": "PTO",
    "definition": "Paid Time Off - Employee benefit for vacation days",
    "category": "benefits",
    "aliases": ["vacation", "time off"],
    "examples": ["Employees get 15 days of PTO per year"]
  }'

# Search terms
curl "http://localhost:8001/glossary/search?query=time&limit=10"

# Export glossary
curl "http://localhost:8001/glossary/export?format=markdown" -o hr_glossary.md
```

### Glossary File Structure

Glossaries are stored in JSON format at `glossaries/{domain}_glossary.json`:

```json
{
  "pto": {
    "term": "PTO",
    "definition": "Paid Time Off...",
    "category": "benefits",
    "aliases": ["vacation"],
    "examples": ["..."],
    "related_terms": ["sick leave"],
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
    "version": 1
  }
}
```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file:

```env
# Domain configuration
DOMAIN_NAME=IT  # Default domain for main.py

# Service ports
EMBEDDING_SERVICE_PORT=8100

# Redis (optional)
REDIS_HOST=localhost
REDIS_PORT=6379

# Sentry error tracking (optional)
SENTRY_DSN=https://your-sentry-dsn

# Environment
ENVIRONMENT=development

# MongoDB configuration
# Add your MongoDB settings here
```

### Performance Tuning

Edit `services/common/performance.py`:

```python
OPTIMIZATION_CONFIG = {
    'enable_caching': True,
    'cache_ttl': 300,  # 5 minutes
    'max_cache_size': 1000,
    'connection_pool_size': 20,
    'batch_size': 50,
    'rate_limit_calls': 100,
    'rate_limit_window': 60  # 1 minute
}
```

## 🐳 Docker Deployment

### Build and Run

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Scale services
docker-compose up -d --scale hr_service=2

# View logs
docker-compose logs -f hr_service
```

### Docker Compose Configuration

The `docker-compose.yml` includes:
- Redis for caching
- Domain services (HR, IT by default)
- Health checks
- Automatic restarts
- Volume mounts for logs

## 📊 Monitoring and Debugging

### Performance Metrics

Access performance metrics at `http://localhost:{port}/metrics`:

```json
{
  "service": "HR",
  "metrics": {
    "chat_request": {
      "count": 150,
      "avg_time": 0.234,
      "min_time": 0.100,
      "max_time": 1.234
    }
  }
}
```

### Error Tracking

1. **Local Development**: Check log files in `logs/` directory
2. **Production**: Configure Sentry DSN for automatic error tracking

### Health Checks

```bash
# Check service health
curl http://localhost:8001/health

# Response
{
  "status": "healthy",
  "service": "HR",
  "timestamp": "2024-01-01T00:00:00",
  "redis_available": true
}
```

## 🔌 Integration Examples

### Python Client

```python
import requests

# Create embedding
response = requests.post("http://localhost:8100/embeddings", json={
    "text": "Hello world",
    "model": "text-embedding-ada-002"
})
embedding = response.json()["embeddings"]

# Query domain service
response = requests.post("http://localhost:8001/chat", json={
    "messages": [{"role": "user", "content": "What is PTO?"}],
    "stream": False
})
answer = response.json()
```

### JavaScript/TypeScript Client

```javascript
// Query with streaming
const response = await fetch('http://localhost:8001/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    messages: [{ role: 'user', content: 'Explain the leave policy' }],
    stream: true
  })
});

const reader = response.body.getReader();
// Process streaming response...
```

## 🛠️ Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   # Find process using port
   lsof -i :8001
   # Or change port in start command
   python start_domain_service.py hr --port 8010
   ```

2. **Import Errors**
   ```bash
   # Ensure all dependencies are installed
   pip install -r requirements.txt
   ```

3. **Redis Connection Failed**
   - Service will run without caching
   - Install and start Redis: `redis-server`

4. **Domain Not Found**
   - Check if domain directory exists in `domains/`
   - Ensure `config.py` is properly formatted

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your domain or feature
4. Submit a pull request

### Adding a Domain Template

To contribute a new domain template:

1. Create domain configuration in `domains/<domain_name>/`
2. Add example templates
3. Document domain-specific features
4. Add to the domain examples in this README

## 📄 License

[Your License Here]

## 🙏 Acknowledgments

Built with:
- FastAPI for high-performance APIs
- LangChain for RAG capabilities
- OpenAI for embeddings and chat
- Redis for caching
- Sentry for error tracking
