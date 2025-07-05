"""
HR Service - FastAPI service for HR domain
"""
import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from common.base_service import BaseService


class HRService(BaseService):
    """HR-specific service implementation"""
    
    def __init__(self, port: int = 8001, host: str = "0.0.0.0"):
        super().__init__(domain_name="HR", port=port, host=host)
        self.logger.info("HR Service initialized")
    
    def _add_routes(self):
        """Add HR-specific routes in addition to common routes"""
        # First add common routes
        super()._add_routes()
        
        # Add HR-specific routes here
        @self.app.get("/hr/info")
        async def hr_info():
            """HR-specific information endpoint"""
            return {
                "service": "HR Service",
                "description": "Human Resources Management Service",
                "capabilities": [
                    "Employee management",
                    "Recruitment processes",
                    "Training and development",
                    "Performance management",
                    "Compensation and benefits"
                ]
            }
        
        @self.app.get("/hr/systems")
        async def hr_systems():
            """Get HR-specific systems information"""
            domain_config = self._get_domain_config()
            return {
                "systems": domain_config.custom_config.get("systems", ""),
                "topics": domain_config.custom_config.get("topics", "")
            }
    
    def _get_domain_config(self):
        """Get HR domain configuration"""
        from domains.context import DomainContext
        return DomainContext.get_config()


def main():
    """Main entry point for HR service"""
    # Get port from environment or use default
    port = int(os.getenv("HR_SERVICE_PORT", 8001))
    service = HRService(port=port)
    service.run()


if __name__ == "__main__":
    main()