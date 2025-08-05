"""
Main FastMCP 2.0 Excel Server with tag-based tool filtering.
"""

import logging
import os
from pathlib import Path
from typing import Optional

# Core components
from .core.config import load_config
from .core.mcp_server import TaggedFastMCP

# Tool registration modules
from .tools.workbook_tools import register_workbook_tools
from .tools.data_tools import register_data_tools
from .tools.sheet_tools import register_sheet_tools
from .tools.format_tools import register_format_tools
from .tools.advanced_tools import register_advanced_tools
from .tools.minio_tools import register_minio_tools

# Setup logging
LOG_FILE = Path(__file__).parent.parent / "excel-mcp.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()  # Also log to console
    ],
)
logger = logging.getLogger("excel-mcp")


class ExcelMCPServer:
    """
    Main Excel MCP Server with tag-based tool filtering.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the Excel MCP server.
        
        Args:
            config_path: Path to configuration file (optional)
        """
        self.config = load_config(config_path)
        self.mcp = TaggedFastMCP("excel-mcp", self.config)
        self._register_all_tools()
    
    def _register_all_tools(self):
        """Register all tool modules with the MCP server."""
        logger.info("Registering tool modules...")
        
        # Register all tool categories
        register_workbook_tools(self.mcp)
        register_data_tools(self.mcp)
        register_sheet_tools(self.mcp)
        register_format_tools(self.mcp)
        register_advanced_tools(self.mcp)
        register_minio_tools(self.mcp)
        
        # Add agent filtering endpoints
        self._register_agent_tools()
        
        logger.info(f"Registered {len(self.mcp._tool_tags)} tools")
    
    def _register_agent_tools(self):
        """Register agent management tools."""
        
        @self.mcp.tool()
        def list_available_tools_for_agent(agent_type: str = None) -> str:
            """
            List tools available to a specific agent type.
            
            Args:
                agent_type: Type of agent ('excel_analyst', 'excel_editor', etc.)
                
            Returns:
                JSON string with available tools for the agent
            """
            try:
                result = self.mcp.filter_tools_for_agent(agent_type)
                import json
                return json.dumps(result, indent=2)
            except Exception as e:
                logger.error(f"Error listing tools for agent: {e}")
                return f"Error: {str(e)}"
        
        @self.mcp.tool()
        def get_agent_profiles() -> str:
            """
            Get list of available predefined agent profiles.
            
            Returns:
                JSON string with available agent profiles
            """
            try:
                from .core.tag_system import AGENT_PROFILES
                profiles = {}
                for key, profile in AGENT_PROFILES.items():
                    profiles[key] = {
                        "name": profile.name,
                        "required_tags": list(profile.required_tags)
                    }
                
                import json
                return json.dumps({
                    "available_profiles": profiles,
                    "total_profiles": len(profiles)
                }, indent=2)
            except Exception as e:
                logger.error(f"Error getting agent profiles: {e}")
                return f"Error: {str(e)}"
    
    def set_agent_context(self, agent_type: str = None, custom_tags: list = None):
        """
        Set the current agent context for tool filtering.
        
        Args:
            agent_type: Predefined agent type
            custom_tags: Custom tags for agent
        """
        self.mcp.set_agent_profile(agent_type, custom_tags)
        logger.info(f"Set agent context: {agent_type or 'custom'}")
    
    def run(self, 
            host: str = None, 
            port: int = None, 
            log_level: str = None,
            agent_type: str = None):
        """
        Start the MCP server.
        
        Args:
            host: Host to bind to (overrides config)
            port: Port to bind to (overrides config)
            log_level: Log level (overrides config)
            agent_type: Default agent type for tool filtering
        """
        # Use provided values or fallback to config
        host = host or self.config.mcp.host
        port = port or self.config.mcp.port
        log_level = log_level or self.config.mcp.log_level
        
        # Set up directory
        os.makedirs(self.config.mcp.excel_files_path, exist_ok=True)
        
        # Set agent context if specified
        if agent_type:
            self.set_agent_context(agent_type=agent_type)
        
        try:
            logger.info(f"Starting Excel MCP server (files directory: {self.config.mcp.excel_files_path})")
            logger.info(f"Host: {host}")
            logger.info(f"Port: {port}")
            logger.info(f"Log level: {log_level}")
            logger.info(f"Total tools registered: {len(self.mcp._tool_tags)}")
            
            if agent_type:
                available_tools = self.mcp.get_available_tools()
                logger.info(f"Agent type: {agent_type}, Available tools: {len(available_tools)}")
            
            self.mcp.run(
                transport="http",
                host=host,
                port=port,
                log_level=log_level,
            )
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
        except Exception as e:
            logger.error(f"Server failed: {e}")
            raise
        finally:
            logger.info("Server shutdown complete")


def main():
    """Main entry point for the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Excel MCP Server with tag-based filtering")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--host", help="Host to bind to")
    parser.add_argument("--port", type=int, help="Port to bind to")
    parser.add_argument("--log-level", help="Log level")
    parser.add_argument("--agent-type", help="Default agent type for tool filtering")
    
    args = parser.parse_args()
    
    server = ExcelMCPServer(config_path=args.config)
    server.run(
        host=args.host,
        port=args.port,
        log_level=args.log_level,
        agent_type=args.agent_type
    )


if __name__ == "__main__":
    main()