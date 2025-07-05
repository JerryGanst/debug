"""
Domain Services Python Client SDK

Easy-to-use client for interacting with domain-based microservices.
"""
import requests
import json
from typing import Dict, List, Any, Optional, Union, Iterator
import asyncio
import aiohttp
from dataclasses import dataclass
from enum import Enum
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class StreamMode(Enum):
    """Streaming mode options"""
    NONE = "none"
    SSE = "sse"
    WEBSOCKET = "websocket"


@dataclass
class DomainConfig:
    """Domain service configuration"""
    name: str
    base_url: str
    port: int
    timeout: int = 30
    headers: Optional[Dict[str, str]] = None


@dataclass
class ChatMessage:
    """Chat message structure"""
    role: str
    content: str


@dataclass
class GlossaryTerm:
    """Glossary term structure"""
    term: str
    definition: str
    category: Optional[str] = None
    aliases: Optional[List[str]] = None
    examples: Optional[List[str]] = None
    related_terms: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class DomainServiceError(Exception):
    """Base exception for domain service errors"""
    pass


class DomainClient:
    """Client for interacting with domain services"""
    
    # Default service configurations
    DEFAULT_SERVICES = {
        "hr": DomainConfig("hr", "http://localhost", 8001),
        "it": DomainConfig("it", "http://localhost", 8002),
        "finance": DomainConfig("finance", "http://localhost", 8003),
        "legal": DomainConfig("legal", "http://localhost", 8004),
        "sales": DomainConfig("sales", "http://localhost", 8005),
        "marketing": DomainConfig("marketing", "http://localhost", 8006),
    }
    
    def __init__(self, domain: str, custom_config: Optional[DomainConfig] = None):
        """
        Initialize domain client
        
        Args:
            domain: Domain name (e.g., 'hr', 'it', 'finance')
            custom_config: Optional custom configuration
        """
        if custom_config:
            self.config = custom_config
        elif domain.lower() in self.DEFAULT_SERVICES:
            self.config = self.DEFAULT_SERVICES[domain.lower()]
        else:
            # Default configuration for unknown domains
            self.config = DomainConfig(
                name=domain,
                base_url="http://localhost",
                port=8000
            )
        
        self.base_url = f"{self.config.base_url}:{self.config.port}"
        self.session = requests.Session()
        if self.config.headers:
            self.session.headers.update(self.config.headers)
    
    # Core API Methods
    
    def health_check(self) -> Dict[str, Any]:
        """Check service health"""
        response = self._get("/health")
        return response.json()
    
    def get_domain_info(self) -> Dict[str, Any]:
        """Get domain configuration information"""
        response = self._get("/domain-info")
        return response.json()
    
    def chat(self, messages: List[Union[ChatMessage, dict]], 
             stream: bool = False, 
             files: Optional[List[str]] = None) -> Union[Dict[str, Any], Iterator[str]]:
        """
        Chat with the AI assistant
        
        Args:
            messages: List of chat messages
            stream: Whether to stream the response
            files: Optional list of file contents
            
        Returns:
            Response dict or iterator for streaming
        """
        # Convert ChatMessage objects to dicts
        msg_dicts = []
        for msg in messages:
            if isinstance(msg, ChatMessage):
                msg_dicts.append({"role": msg.role, "content": msg.content})
            else:
                msg_dicts.append(msg)
        
        payload = {
            "messages": msg_dicts,
            "stream": stream
        }
        if files:
            payload["file"] = files
        
        if stream:
            return self._stream_post("/chat", payload)
        else:
            response = self._post("/chat", payload)
            return response.json()
    
    def query(self, question: str, context: Optional[str] = None) -> Iterator[str]:
        """
        Query using RAG
        
        Args:
            question: Query text
            context: Optional additional context
            
        Returns:
            Iterator yielding response chunks
        """
        payload = {"question": question}
        if context:
            payload["context"] = context
        
        return self._stream_post("/query", payload)
    
    def summarize(self, text: str) -> Dict[str, Any]:
        """
        Summarize text
        
        Args:
            text: Text to summarize
            
        Returns:
            Summary response
        """
        response = self._post("/summarize", {"question": text})
        return response.json()
    
    def translate(self, text: str, target_language: str) -> Iterator[str]:
        """
        Translate text
        
        Args:
            text: Source text
            target_language: Target language (中文, 英文, 越南语, 西班牙语)
            
        Returns:
            Iterator yielding translated text
        """
        payload = {
            "source_text": text,
            "target_language": target_language
        }
        return self._stream_post("/translate", payload)
    
    def calculate_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate similarity between two texts
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0-1)
        """
        response = self._post("/similarity", {
            "str1": text1,
            "str2": text2
        })
        return response.json()["score"]
    
    # Glossary Management Methods
    
    def add_glossary_term(self, term: Union[GlossaryTerm, dict]) -> Dict[str, Any]:
        """Add a term to the glossary"""
        if isinstance(term, GlossaryTerm):
            payload = {
                "term": term.term,
                "definition": term.definition,
                "category": term.category,
                "aliases": term.aliases,
                "examples": term.examples,
                "related_terms": term.related_terms,
                "metadata": term.metadata
            }
        else:
            payload = term
        
        response = self._post("/glossary/terms", payload)
        return response.json()
    
    def get_glossary_term(self, term: str) -> Optional[Dict[str, Any]]:
        """Get a specific term from the glossary"""
        try:
            response = self._get(f"/glossary/terms/{term}")
            return response.json()
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def update_glossary_term(self, term: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing term"""
        response = self._put(f"/glossary/terms/{term}", updates)
        return response.json()
    
    def delete_glossary_term(self, term: str) -> bool:
        """Delete a term from the glossary"""
        response = self._delete(f"/glossary/terms/{term}")
        return response.status_code == 200
    
    def search_glossary(self, query: str, 
                       category: Optional[str] = None, 
                       limit: int = 10) -> List[Dict[str, Any]]:
        """Search glossary terms"""
        params = {"query": query, "limit": limit}
        if category:
            params["category"] = category
        
        response = self._get("/glossary/search", params=params)
        return response.json()
    
    def list_glossary_terms(self, 
                           category: Optional[str] = None,
                           page: int = 1,
                           page_size: int = 50) -> Dict[str, Any]:
        """List all glossary terms with pagination"""
        params = {"page": page, "page_size": page_size}
        if category:
            params["category"] = category
        
        response = self._get("/glossary/terms", params=params)
        return response.json()
    
    def export_glossary(self, format: str = "json") -> Union[Dict[str, Any], str]:
        """Export glossary in specified format"""
        response = self._get("/glossary/export", params={"format": format})
        
        if format == "json":
            return response.json()
        else:
            return response.text
    
    def import_glossary(self, data: Dict[str, Any], merge: bool = False) -> Dict[str, Any]:
        """Import glossary data"""
        response = self._post("/glossary/import", data, params={"merge": merge})
        return response.json()
    
    # Monitoring Methods
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        response = self._get("/metrics")
        return response.json()
    
    # Async Methods
    
    async def achat(self, messages: List[Union[ChatMessage, dict]], 
                    stream: bool = False,
                    files: Optional[List[str]] = None) -> Union[Dict[str, Any], AsyncIterator[str]]:
        """Async version of chat"""
        async with aiohttp.ClientSession() as session:
            msg_dicts = []
            for msg in messages:
                if isinstance(msg, ChatMessage):
                    msg_dicts.append({"role": msg.role, "content": msg.content})
                else:
                    msg_dicts.append(msg)
            
            payload = {"messages": msg_dicts, "stream": stream}
            if files:
                payload["file"] = files
            
            if stream:
                async for chunk in self._async_stream_post(session, "/chat", payload):
                    yield chunk
            else:
                async with session.post(f"{self.base_url}/chat", json=payload) as response:
                    return await response.json()
    
    # Private Helper Methods
    
    def _get(self, endpoint: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make GET request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.get(url, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        return response
    
    def _post(self, endpoint: str, data: Dict[str, Any], 
              params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make POST request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data, params=params, timeout=self.config.timeout)
        response.raise_for_status()
        return response
    
    def _put(self, endpoint: str, data: Dict[str, Any]) -> requests.Response:
        """Make PUT request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.put(url, json=data, timeout=self.config.timeout)
        response.raise_for_status()
        return response
    
    def _delete(self, endpoint: str) -> requests.Response:
        """Make DELETE request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.delete(url, timeout=self.config.timeout)
        response.raise_for_status()
        return response
    
    def _stream_post(self, endpoint: str, data: Dict[str, Any]) -> Iterator[str]:
        """Make streaming POST request"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.post(url, json=data, stream=True, timeout=self.config.timeout)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line_str = line.decode('utf-8')
                if line_str.startswith('data: '):
                    data = line_str[6:]
                    if data != '[DONE]':
                        yield data
    
    async def _async_stream_post(self, session: aiohttp.ClientSession, 
                                endpoint: str, data: Dict[str, Any]) -> AsyncIterator[str]:
        """Make async streaming POST request"""
        url = f"{self.base_url}{endpoint}"
        async with session.post(url, json=data) as response:
            async for line in response.content:
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        data = line_str[6:]
                        if data != '[DONE]':
                            yield data


class MultiDomainClient:
    """Client for working with multiple domains"""
    
    def __init__(self, domains: List[str]):
        """
        Initialize multi-domain client
        
        Args:
            domains: List of domain names
        """
        self.clients = {domain: DomainClient(domain) for domain in domains}
    
    def query_all(self, question: str) -> Dict[str, Any]:
        """Query all domains and aggregate results"""
        results = {}
        for domain, client in self.clients.items():
            try:
                # Collect streaming results
                chunks = []
                for chunk in client.query(question):
                    chunks.append(chunk)
                results[domain] = ''.join(chunks)
            except Exception as e:
                logger.error(f"Error querying {domain}: {str(e)}")
                results[domain] = {"error": str(e)}
        
        return results
    
    def search_all_glossaries(self, query: str, limit: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """Search across all domain glossaries"""
        results = {}
        for domain, client in self.clients.items():
            try:
                results[domain] = client.search_glossary(query, limit=limit)
            except Exception as e:
                logger.error(f"Error searching {domain} glossary: {str(e)}")
                results[domain] = []
        
        return results


# Convenience functions

def quick_chat(domain: str, message: str) -> str:
    """Quick single-message chat"""
    client = DomainClient(domain)
    response = client.chat([{"role": "user", "content": message}])
    return response.get("response", "")


def quick_query(domain: str, question: str) -> str:
    """Quick query with streaming response collection"""
    client = DomainClient(domain)
    chunks = []
    for chunk in client.query(question):
        chunks.append(chunk)
    return ''.join(chunks)


# Example usage
if __name__ == "__main__":
    # Example 1: Simple chat
    hr_client = DomainClient("hr")
    response = hr_client.chat([
        ChatMessage("user", "What is the vacation policy?")
    ])
    print("Chat response:", response)
    
    # Example 2: Add glossary term
    term = GlossaryTerm(
        term="PTO",
        definition="Paid Time Off",
        category="benefits",
        examples=["Employees get 15 days of PTO annually"]
    )
    hr_client.add_glossary_term(term)
    
    # Example 3: Multi-domain search
    multi_client = MultiDomainClient(["hr", "it", "finance"])
    results = multi_client.search_all_glossaries("policy")
    print("Multi-domain search results:", results)
    
    # Example 4: Async streaming chat
    async def async_chat_example():
        client = DomainClient("it")
        async for chunk in client.achat(
            [ChatMessage("user", "Explain our IT security policy")],
            stream=True
        ):
            print(chunk, end='', flush=True)
    
    # Run async example
    # asyncio.run(async_chat_example())