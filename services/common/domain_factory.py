"""
Domain Factory - Dynamically create services for any domain
"""
import os
import sys
from typing import Dict, Any, Optional, List
import importlib
import logging

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from services.common.base_service import BaseService

logger = logging.getLogger(__name__)


class DomainServiceFactory:
    """Factory for creating domain-specific services dynamically"""
    
    @staticmethod
    def create_service(domain_name: str, port: int, host: str = "0.0.0.0") -> BaseService:
        """
        Create a service for any domain
        
        Args:
            domain_name: Name of the domain (e.g., 'hr', 'it', 'finance', etc.)
            port: Port to run the service on
            host: Host address
            
        Returns:
            Domain-specific service instance
        """
        # Try to load domain-specific service class
        service_class = DomainServiceFactory._load_domain_service_class(domain_name)
        
        if service_class:
            # Use domain-specific service class
            return service_class(port=port, host=host)
        else:
            # Use generic domain service
            return GenericDomainService(domain_name=domain_name, port=port, host=host)
    
    @staticmethod
    def _load_domain_service_class(domain_name: str):
        """Try to load a domain-specific service class"""
        try:
            # Convert domain name to module name (e.g., 'hr' -> 'hr_service')
            module_name = f"services.{domain_name.lower()}.{domain_name.lower()}_service"
            class_name = f"{domain_name.upper()}Service"
            
            # Try to import the module
            module = importlib.import_module(module_name)
            
            # Get the service class
            service_class = getattr(module, class_name, None)
            
            if service_class:
                logger.info(f"Loaded custom service class for domain: {domain_name}")
                return service_class
        except (ImportError, AttributeError) as e:
            logger.info(f"No custom service class found for domain {domain_name}, using generic service")
        
        return None
    
    @staticmethod
    def get_available_domains() -> List[str]:
        """Get list of available domains by scanning the domains directory"""
        domains = []
        domains_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
            'domains'
        )
        
        if os.path.exists(domains_path):
            for item in os.listdir(domains_path):
                item_path = os.path.join(domains_path, item)
                # Check if it's a directory with a config.py file
                if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, 'config.py')):
                    domains.append(item)
        
        return domains


class GenericDomainService(BaseService):
    """Generic domain service for domains without custom implementation"""
    
    def __init__(self, domain_name: str, port: int, host: str = "0.0.0.0"):
        # Capitalize domain name properly
        formatted_domain = domain_name.upper() if domain_name else "GENERIC"
        super().__init__(domain_name=formatted_domain, port=port, host=host)
        self.logger.info(f"Generic {formatted_domain} Service initialized")
    
    def _add_routes(self):
        """Add generic domain routes in addition to common routes"""
        # First add common routes
        super()._add_routes()
        
        # Add generic domain info route
        domain_lower = self.domain_name.lower()
        
        @self.app.get(f"/{domain_lower}/info")
        async def domain_info():
            """Domain-specific information endpoint"""
            domain_config = self._get_domain_config()
            return {
                "service": f"{self.domain_name} Service",
                "description": f"{self.domain_name} Domain Management Service",
                "domain_config": domain_config.custom_config if domain_config else {},
                "capabilities": self._get_domain_capabilities()
            }
        
        @self.app.get(f"/{domain_lower}/config")
        async def domain_config():
            """Get domain configuration"""
            domain_config = self._get_domain_config()
            if domain_config:
                return {
                    "domain_name": domain_config.DOMAIN_NAME,
                    "doc_type": domain_config.DOMAIN_DOC_TYPE,
                    "custom_config": domain_config.custom_config,
                }
            return {"error": "Domain configuration not found"}
    
    def _get_domain_config(self):
        """Get domain configuration"""
        try:
            from domains.context import DomainContext
            return DomainContext.get_config()
        except Exception as e:
            self.logger.error(f"Error getting domain config: {str(e)}")
            return None
    
    def _get_domain_capabilities(self) -> List[str]:
        """Get domain capabilities based on configuration"""
        domain_config = self._get_domain_config()
        if domain_config and hasattr(domain_config, 'custom_config'):
            topics = domain_config.custom_config.get('topics', '')
            if topics:
                return [topic.strip() for topic in topics.split('、')]
        
        # Default capabilities
        return [
            "Document management",
            "Query processing",
            "Knowledge base access",
            "Custom glossary management"
        ]


def create_service_for_domain(domain_name: str, port: Optional[int] = None) -> BaseService:
    """
    Convenience function to create a service for a domain
    
    Args:
        domain_name: Name of the domain
        port: Port number (if None, will use default based on domain)
        
    Returns:
        Service instance
    """
    if port is None:
        # Assign default ports based on domain
        default_ports = {
            'hr': 8001,
            'it': 8002,
            'finance': 8003,
            'legal': 8004,
            'sales': 8005,
            'marketing': 8006,
            # Add more as needed
        }
        port = default_ports.get(domain_name.lower(), 8000)
    
    return DomainServiceFactory.create_service(domain_name, port)