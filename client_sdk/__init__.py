"""
Domain Services Client SDK

Easy-to-use Python client for domain-based microservices.
"""

from .domain_client import (
    DomainClient,
    MultiDomainClient,
    DomainConfig,
    ChatMessage,
    GlossaryTerm,
    DomainServiceError,
    StreamMode,
    quick_chat,
    quick_query
)

__version__ = "1.0.0"
__all__ = [
    "DomainClient",
    "MultiDomainClient", 
    "DomainConfig",
    "ChatMessage",
    "GlossaryTerm",
    "DomainServiceError",
    "StreamMode",
    "quick_chat",
    "quick_query"
]