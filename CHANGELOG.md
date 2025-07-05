# Changelog

## Version 2.0.0 - Domain-Based Microservices Architecture

### Major Changes

#### 🏗️ Architecture Refactoring

1. **Flexible Domain System**
   - Removed hardcoded HR/IT domain restrictions
   - Domains are now dynamically configurable
   - Easy to add new domains without code changes
   - Generic domain service factory for automatic service creation

2. **Separated Services**
   - Each domain runs as an independent FastAPI service on its own port
   - Embedding service separated into standalone microservice (port 8100)
   - Services can be scaled independently

3. **Removed Components**
   - Removed vllm service (to be moved to separate project)
   - Removed hardcoded start_hr_service.py and start_it_service.py scripts

#### ✨ New Features

1. **Custom Glossary Management**
   - Users can add, update, delete custom terms per domain
   - Full CRUD API for glossary operations
   - Import/export functionality (JSON, CSV, Markdown)
   - Search and categorization support
   - Version tracking for terms

2. **Performance Optimizations**
   - Redis caching for non-streaming endpoints
   - GZip compression for responses
   - Parallel processing for embeddings
   - Connection pooling utilities
   - Request timing headers
   - Performance metrics endpoint

3. **Error Reporting**
   - Sentry integration for production error tracking
   - Structured logging to files and console
   - Request ID tracking
   - Performance monitoring
   - Custom error middleware

4. **Python Client SDK**
   - Full-featured client library
   - Async support
   - Type hints
   - Multi-domain operations
   - Easy installation via pip

#### 📝 Documentation

1. **Comprehensive README**
   - Quick start guide
   - Architecture overview
   - API documentation links
   - Integration examples

2. **API Reference** (`docs/API_REFERENCE.md`)
   - Detailed endpoint documentation
   - Request/response examples
   - Error codes
   - Rate limiting info

3. **Domain Addition Guide** (`docs/ADDING_NEW_DOMAINS.md`)
   - Step-by-step instructions
   - Configuration examples
   - Best practices
   - Template examples

#### 🔧 Configuration

1. **Flexible Environment Variables**
   - Domain-agnostic configuration
   - Support for unlimited domains
   - Easy port assignment

2. **Docker Compose Updates**
   - Dynamic domain service configuration
   - Embedding service included
   - Environment variable support

#### 🛠️ Scripts and Tools

1. **Generic Domain Starter**
   - `start_domain_service.py` - Start any domain on any port
   - `--list-domains` option to see available domains

2. **Flexible Multi-Service Starter**
   - `start_all_services.py` - Start multiple domains
   - Command line configuration: `python start_all_services.py finance:8003 legal:8004`
   - Optional embedding service

3. **Migration Script**
   - `migrate_to_services.py` - Help transition from old architecture

### Breaking Changes

1. Domain services now use generic starter script instead of domain-specific scripts
2. Embedding functionality moved to separate service
3. Docker compose service names changed from `hr_service`/`it_service` to `domain_service_1`/`domain_service_2`

### Migration Guide

1. Update `.env` file with new format (see `.env.example`)
2. Run `python migrate_to_services.py` for migration assistance
3. Update client code to use new endpoints if needed
4. Install client SDK for easier integration

### Dependencies Added

- `redis~=5.0.1` - Caching layer
- `sentry-sdk~=1.40.0` - Error tracking
- `numpy~=1.24.3` - Embedding calculations
- `aiohttp~=3.9.1` - Async HTTP client

### Future Enhancements

- Authentication and authorization
- API Gateway for unified entry point
- Service mesh integration
- Kubernetes deployment configs
- GraphQL API option
- WebSocket support for real-time features