"""
IT Service - FastAPI service for IT domain
"""
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.base_service import BaseService


class ITService(BaseService):
    """IT-specific service implementation"""
    
    def __init__(self, port: int = 8002, host: str = "0.0.0.0"):
        super().__init__(domain_name="IT", port=port, host=host)
        self.logger.info("IT Service initialized")
    
    def _add_routes(self):
        """Add IT-specific routes in addition to common routes"""
        # First add common routes
        super()._add_routes()
        
        # Add IT-specific routes here
        @self.app.get("/it/info")
        async def it_info():
            """IT-specific information endpoint"""
            return {
                "service": "IT Service",
                "description": "Information Technology Management Service",
                "capabilities": [
                    "Technical support",
                    "System development",
                    "IT policies",
                    "Data security",
                    "Network management"
                ]
            }
        
        @self.app.get("/it/systems")
        async def it_systems():
            """Get IT-specific systems information"""
            domain_config = self._get_domain_config()
            return {
                "systems": domain_config.custom_config.get("systems", ""),
                "topics": domain_config.custom_config.get("topics", "")
            }
        
        @self.app.get("/it/status")
        async def system_status():
            """Check status of various IT systems"""
            # This could be expanded to actually check system health
            return {
                "ldp": "operational",
                "mes": "operational",
                "sap": "operational",
                "oa": "operational",
                "luxlink": "operational",
                "status_timestamp": self._get_timestamp()
            }
    
    def _get_domain_config(self):
        """Get IT domain configuration"""
        from domains.context import DomainContext
        return DomainContext.get_config()
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


def main():
    """Main entry point for IT service"""
    # Get port from environment or use default
    port = int(os.getenv("IT_SERVICE_PORT", 8002))
    service = ITService(port=port)
    service.run()


if __name__ == "__main__":
    main()