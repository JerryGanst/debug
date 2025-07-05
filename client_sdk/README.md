# Domain Services Client SDK

A Python client library for interacting with domain-based microservices.

## Installation

```bash
pip install domain-services-client
```

Or install from source:

```bash
cd client_sdk
pip install -e .
```

## Quick Start

```python
from domain_client import DomainClient, ChatMessage

# Initialize client for a specific domain
client = DomainClient("hr")

# Simple chat
response = client.chat([
    ChatMessage("user", "What is the vacation policy?")
])
print(response)

# Query with RAG
for chunk in client.query("How do I apply for leave?"):
    print(chunk, end='', flush=True)
```

## Features

- **Easy-to-use API**: Simple methods for all endpoints
- **Streaming support**: Handle streaming responses efficiently
- **Async support**: Full async/await support for better performance
- **Type hints**: Complete type annotations for better IDE support
- **Multi-domain**: Work with multiple domains simultaneously
- **Glossary management**: Full CRUD operations for domain glossaries

## Usage Examples

### Basic Chat

```python
from domain_client import DomainClient, ChatMessage

client = DomainClient("finance")

# Single message
response = client.chat([
    ChatMessage("user", "What is our expense policy?")
])

# Multi-turn conversation
messages = [
    ChatMessage("user", "What is our expense policy?"),
    ChatMessage("assistant", "Our expense policy requires..."),
    ChatMessage("user", "What about international travel?")
]
response = client.chat(messages)
```

### Streaming Chat

```python
# Stream responses
for chunk in client.chat(messages, stream=True):
    print(chunk, end='', flush=True)
```

### Glossary Management

```python
from domain_client import GlossaryTerm

# Add a term
term = GlossaryTerm(
    term="ROI",
    definition="Return on Investment",
    category="finance",
    examples=["The ROI for this project is 25%"],
    aliases=["return on investment", "investment return"]
)
client.add_glossary_term(term)

# Search terms
results = client.search_glossary("investment", limit=10)

# Update a term
client.update_glossary_term("ROI", {
    "definition": "Return on Investment - A measure of profitability"
})

# Export glossary
glossary_data = client.export_glossary(format="json")
```

### Async Operations

```python
import asyncio
from domain_client import DomainClient, ChatMessage

async def async_example():
    client = DomainClient("it")
    
    # Async chat
    response = await client.achat([
        ChatMessage("user", "Explain our security policy")
    ])
    print(response)
    
    # Async streaming
    async for chunk in client.achat(messages, stream=True):
        print(chunk, end='', flush=True)

# Run async example
asyncio.run(async_example())
```

### Multi-Domain Operations

```python
from domain_client import MultiDomainClient

# Work with multiple domains
multi_client = MultiDomainClient(["hr", "it", "finance"])

# Query all domains
results = multi_client.query_all("What is the policy on remote work?")
for domain, response in results.items():
    print(f"\n{domain.upper()} Response:")
    print(response)

# Search all glossaries
glossary_results = multi_client.search_all_glossaries("policy")
```

### Custom Configuration

```python
from domain_client import DomainClient, DomainConfig

# Custom domain configuration
config = DomainConfig(
    name="custom",
    base_url="https://api.mycompany.com",
    port=443,
    timeout=60,
    headers={"Authorization": "Bearer token"}
)

client = DomainClient("custom", custom_config=config)
```

## API Reference

### DomainClient

Main client class for interacting with a domain service.

#### Methods

- `health_check()` - Check service health
- `get_domain_info()` - Get domain configuration
- `chat(messages, stream=False, files=None)` - Chat with AI
- `query(question, context=None)` - Query with RAG
- `summarize(text)` - Summarize text
- `translate(text, target_language)` - Translate text
- `calculate_similarity(text1, text2)` - Calculate text similarity
- `add_glossary_term(term)` - Add glossary term
- `get_glossary_term(term)` - Get specific term
- `update_glossary_term(term, updates)` - Update term
- `delete_glossary_term(term)` - Delete term
- `search_glossary(query, category=None, limit=10)` - Search terms
- `list_glossary_terms(category=None, page=1, page_size=50)` - List terms
- `export_glossary(format="json")` - Export glossary
- `import_glossary(data, merge=False)` - Import glossary
- `get_metrics()` - Get performance metrics

### MultiDomainClient

Client for working with multiple domains simultaneously.

#### Methods

- `query_all(question)` - Query all domains
- `search_all_glossaries(query, limit=5)` - Search all glossaries

### Data Classes

- `ChatMessage(role: str, content: str)` - Chat message
- `GlossaryTerm(...)` - Glossary term structure
- `DomainConfig(...)` - Domain configuration

## Error Handling

```python
from domain_client import DomainServiceError

try:
    response = client.chat(messages)
except DomainServiceError as e:
    print(f"Service error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Command Line Tools

The SDK includes command-line tools:

```bash
# Quick chat
domain-chat hr "What is the vacation policy?"

# Quick query
domain-query finance "Show me the Q4 financial report"
```

## Development

### Running Tests

```bash
pip install -e .[dev]
pytest tests/
```

### Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License - see LICENSE file for details