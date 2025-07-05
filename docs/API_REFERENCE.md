# API Reference

This document provides detailed information about all available API endpoints across the domain services and embedding service.

## Domain Services API

All domain services share a common set of endpoints. Replace `{domain}` with your specific domain (e.g., hr, it, finance).

### Base URL
- Development: `http://localhost:{port}`
- Production: `https://api.yourdomain.com/{domain}`

### Authentication
Currently, the API does not require authentication. In production, you should implement appropriate authentication mechanisms.

### Common Headers
```http
Content-Type: application/json
Accept: application/json
```

---

## Core Endpoints

### Health Check
Check if the service is running and healthy.

```http
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "service": "HR",
  "timestamp": "2024-01-01T00:00:00.000Z",
  "redis_available": true
}
```

### Domain Information
Get information about the current domain configuration.

```http
GET /domain-info
```

**Response:**
```json
{
  "domain_name": "HR",
  "doc_type": "HR Infos",
  "custom_config": {
    "topics": "人力资源政策、招聘流程、培训发展、绩效管理、薪酬福利",
    "systems": "智慧人资、OA、i学堂"
  }
}
```

---

## Chat and Query Endpoints

### Chat
Interactive chat with the AI assistant.

```http
POST /chat
```

**Request Body:**
```json
{
  "messages": [
    {
      "role": "user",
      "content": "What is the vacation policy?"
    }
  ],
  "stream": false,
  "file": ["optional file content"]
}
```

**Response (Non-streaming):**
```json
{
  "response": "The vacation policy allows...",
  "sources": ["document1.pdf", "document2.pdf"]
}
```

**Response (Streaming):**
Server-Sent Events (SSE) format:
```
data: {"chunk": "The vacation ", "type": "text"}
data: {"chunk": "policy allows...", "type": "text"}
data: {"sources": ["document1.pdf"], "type": "sources"}
data: [DONE]
```

### Query
Process a query using RAG (Retrieval-Augmented Generation).

```http
POST /query
```

**Request Body:**
```json
{
  "question": "How do I apply for leave?",
  "context": "optional additional context"
}
```

**Response:**
Streaming response in SSE format.

### Summarize
Summarize text or documents.

```http
POST /summarize
```

**Request Body:**
```json
{
  "question": "Text to summarize..."
}
```

**Response:**
```json
{
  "summary": "This text discusses...",
  "key_points": ["point1", "point2"]
}
```

### Translate
Translate text between languages.

```http
POST /translate
```

**Request Body:**
```json
{
  "source_text": "Hello, how are you?",
  "target_language": "中文"
}
```

**Supported Languages:**
- 中文 (Chinese)
- 英文 (English)
- 越南语 (Vietnamese)
- 西班牙语 (Spanish)

**Response:**
Streaming response with translated text.

### Calculate Similarity
Calculate similarity between two texts.

```http
POST /similarity
```

**Request Body:**
```json
{
  "str1": "First text",
  "str2": "Second text"
}
```

**Response:**
```json
{
  "score": 0.85
}
```

---

## Glossary Management Endpoints

### Create Term
Add a new term to the domain glossary.

```http
POST /glossary/terms
```

**Request Body:**
```json
{
  "term": "API",
  "definition": "Application Programming Interface",
  "category": "technology",
  "aliases": ["Application Interface"],
  "examples": ["REST API", "GraphQL API"],
  "related_terms": ["REST", "HTTP"],
  "metadata": {
    "source": "Technical Documentation",
    "approved": true
  }
}
```

**Response:**
```json
{
  "term": "API",
  "definition": "Application Programming Interface",
  "category": "technology",
  "aliases": ["Application Interface"],
  "examples": ["REST API", "GraphQL API"],
  "related_terms": ["REST", "HTTP"],
  "metadata": {
    "source": "Technical Documentation",
    "approved": true
  },
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "version": 1
}
```

### Get Term
Retrieve a specific term from the glossary.

```http
GET /glossary/terms/{term}
```

**Parameters:**
- `term` (path): The term to retrieve

**Response:**
Same as create term response.

### Update Term
Update an existing term.

```http
PUT /glossary/terms/{term}
```

**Request Body:**
```json
{
  "definition": "Updated definition",
  "examples": ["New example"]
}
```

**Response:**
Updated term object with incremented version.

### Delete Term
Remove a term from the glossary.

```http
DELETE /glossary/terms/{term}
```

**Response:**
```json
{
  "message": "Term 'API' deleted successfully"
}
```

### Search Terms
Search for terms in the glossary.

```http
GET /glossary/search?query={query}&category={category}&limit={limit}
```

**Query Parameters:**
- `query` (required): Search query
- `category` (optional): Filter by category
- `limit` (optional, default: 10): Maximum results

**Response:**
```json
[
  {
    "term": "API",
    "definition": "...",
    "category": "technology",
    "score": 0.95
  }
]
```

### List All Terms
Get paginated list of all terms.

```http
GET /glossary/terms?category={category}&page={page}&page_size={page_size}
```

**Query Parameters:**
- `category` (optional): Filter by category
- `page` (optional, default: 1): Page number
- `page_size` (optional, default: 50): Items per page

**Response:**
```json
{
  "items": [
    {
      "term": "API",
      "definition": "...",
      "category": "technology"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_items": 150,
    "total_pages": 3,
    "has_next": true,
    "has_prev": false
  }
}
```

### Export Glossary
Export glossary in different formats.

```http
GET /glossary/export?format={format}
```

**Query Parameters:**
- `format`: Export format (json, csv, markdown)

**Response:**
- JSON: Glossary object
- CSV: CSV file download
- Markdown: Markdown file download

### Import Glossary
Import glossary data.

```http
POST /glossary/import?merge={merge}
```

**Query Parameters:**
- `merge` (optional, default: false): Merge with existing data

**Request Body:**
```json
{
  "term_key": {
    "term": "Term Name",
    "definition": "Term definition",
    "category": "category"
  }
}
```

**Response:**
```json
{
  "message": "Glossary imported successfully"
}
```

### Glossary Statistics
Get statistics about the glossary.

```http
GET /glossary/stats
```

**Response:**
```json
{
  "total_terms": 150,
  "total_categories": 5,
  "terms_per_category": {
    "technology": 50,
    "business": 40
  },
  "most_connected_terms": [
    {"term": "API", "connections": 10}
  ],
  "last_updated": "2024-01-01T00:00:00"
}
```

---

## Monitoring Endpoints

### Performance Metrics
Get performance metrics for the service.

```http
GET /metrics
```

**Response:**
```json
{
  "service": "HR",
  "timestamp": "2024-01-01T00:00:00",
  "metrics": {
    "chat_request": {
      "count": 1000,
      "total_time": 234.5,
      "min_time": 0.1,
      "max_time": 2.5,
      "avg_time": 0.234
    }
  },
  "redis_available": true
}
```

### Test Error
Test error handling (development only).

```http
GET /test_error
```

**Response:**
```json
{
  "error": "这是用于测试抛出异常的例子"
}
```

---

## Embedding Service API

The embedding service runs separately on port 8100.

### Base URL
- Development: `http://localhost:8100`
- Production: `https://embeddings.yourdomain.com`

### Generate Embeddings
Generate embeddings for text.

```http
POST /embeddings
```

**Request Body:**
```json
{
  "text": "Sample text to embed",
  "model": "text-embedding-ada-002",
  "use_cache": true
}
```

Or for multiple texts:
```json
{
  "text": ["Text 1", "Text 2", "Text 3"],
  "model": "text-embedding-ada-002",
  "use_cache": true
}
```

**Response:**
```json
{
  "embeddings": [0.001, -0.023, ...],  // or array of arrays for multiple texts
  "model": "text-embedding-ada-002",
  "usage": {
    "prompt_tokens": 10,
    "total_tokens": 10
  },
  "cached": false
}
```

### Batch Embeddings
Process large batches of text efficiently.

```http
POST /embeddings/batch
```

**Request Body:**
```json
{
  "texts": ["Text 1", "Text 2", "..."],
  "model": "text-embedding-ada-002",
  "batch_size": 50,
  "use_cache": true
}
```

**Response:**
```json
{
  "embeddings": [[0.001, ...], [0.002, ...]],
  "model": "text-embedding-ada-002",
  "usage": {
    "prompt_tokens": 500,
    "total_tokens": 500,
    "cached_embeddings": 20,
    "new_embeddings": 30
  },
  "cached": true
}
```

### Calculate Similarity
Calculate similarity between two texts.

```http
POST /similarity
```

**Request Body:**
```json
{
  "text1": "First text",
  "text2": "Second text",
  "model": "text-embedding-ada-002"
}
```

**Response:**
```json
{
  "similarity": 0.85,
  "model": "text-embedding-ada-002"
}
```

### List Models
Get available embedding models.

```http
GET /models
```

**Response:**
```json
{
  "models": [
    {
      "id": "text-embedding-ada-002",
      "description": "OpenAI's text-embedding-ada-002 model",
      "dimensions": 1536
    },
    {
      "id": "text-embedding-3-small",
      "description": "OpenAI's smaller embedding model",
      "dimensions": 1536
    },
    {
      "id": "text-embedding-3-large",
      "description": "OpenAI's larger embedding model",
      "dimensions": 3072
    }
  ]
}
```

### Cache Statistics
Get embedding cache statistics.

```http
GET /cache/stats
```

**Response:**
```json
{
  "total_entries": 1000,
  "cache_hits": 850,
  "cache_misses": 150,
  "hit_rate": 0.85,
  "memory_usage": "256MB"
}
```

### Clear Cache
Clear the embedding cache.

```http
POST /cache/clear
```

**Response:**
```json
{
  "message": "Cache cleared successfully"
}
```

---

## Error Responses

All endpoints may return error responses in the following format:

```json
{
  "error": "Error message",
  "detail": "Detailed error description",
  "request_id": "uuid-string"
}
```

**Common HTTP Status Codes:**
- `200`: Success
- `400`: Bad Request - Invalid input
- `404`: Not Found - Resource not found
- `422`: Unprocessable Entity - Validation error
- `429`: Too Many Requests - Rate limit exceeded
- `500`: Internal Server Error

---

## Rate Limiting

API calls are rate-limited to prevent abuse:
- Default: 100 requests per minute
- Batch operations: 10 requests per minute

Rate limit information is included in response headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

## Streaming Responses

Endpoints that support streaming return Server-Sent Events (SSE):

```javascript
const eventSource = new EventSource('/chat', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({messages: [...], stream: true})
});

eventSource.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data === '[DONE]') {
    eventSource.close();
  } else {
    console.log(data.chunk);
  }
};
```

---

## Performance Headers

All responses include performance metrics:
```http
X-Process-Time: 0.234
X-Cache-Status: HIT|MISS
X-Request-ID: uuid-string
```