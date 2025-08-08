"""
Main FastMCP 2.0 Excel Server.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Set, Any, Optional

# Core components
from .config import load_config
from .file_manager import FileManager
from fastmcp import FastMCP

# Tool registration modules
from ..tools.excel_read import register_excel_read_tools
from ..tools.excel_write import register_excel_write_tools
from ..tools.minio_tools import register_minio_tools

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


class SimpleFastMCP:
    """
    Simple FastMCP server wrapper.
    """
    
    def __init__(self, name: str, config_path: str = None):
        """
        Initialize the MCP server.
        
        Args:
            name: Name of the server
            config_path: Path to configuration file (optional)
        """
        self.config = load_config(config_path)
        self._mcp = FastMCP(name)
        self.file_manager = FileManager(self.config)
        self._register_all_tools()
    
    def _register_all_tools(self):
        """Register all tool modules with the MCP server."""
        logger.info("Registering tool modules...")
        
        # Register all tool categories
        register_excel_read_tools(self)
        register_excel_write_tools(self)
        register_minio_tools(self)
        
        logger.info("Registered tools")
    
    def tool(self, **kwargs):
        """
        Decorator for registering tools.
        
        Args:
            **kwargs: Arguments passed to FastMCP tool decorator
        """
        def decorator(func):
            # Register with FastMCP
            decorated_func = self._mcp.tool(**kwargs)(func)
            return decorated_func
        
        return decorator
    
    def run(self, 
            host: str = None, 
            port: int = None, 
            log_level: str = None):
        """
        Start the MCP server.
        
        Args:
            host: Host to bind to (overrides config)
            port: Port to bind to (overrides config)
            log_level: Log level (overrides config)
        """
        # Use provided values or fallback to config
        host = host or self.config.mcp.host
        port = port or self.config.mcp.port
        log_level = log_level or self.config.mcp.log_level
        
        # Set up directory
        os.makedirs(self.config.mcp.excel_files_path, exist_ok=True)
        
        try:
            logger.info(f"Starting Excel MCP server (files directory: {self.config.mcp.excel_files_path})")
            logger.info(f"Host: {host}")
            logger.info(f"Port: {port}")
            logger.info(f"Log level: {log_level}")
            
            self._mcp.run(
                transport="http",
                host=host,
                port=port,
                log_level=log_level,
            )
        except KeyboardInterrupt:
            logger.info("Server stopped by user")
            # Clean up temporary files
            try:
                import shutil
                if hasattr(self, 'config') and hasattr(self.config, 'mcp') and hasattr(self.config.mcp, 'excel_files_path'):
                    excel_files_dir = Path(self.config.mcp.excel_files_path)
                    if excel_files_dir.exists():
                        # Remove all user directories under excel_files_path
                        for item in excel_files_dir.iterdir():
                            if item.is_dir():
                                shutil.rmtree(item)
                                logger.info(f"Removed temporary directory: {item}")
            except Exception as cleanup_error:
                logger.error(f"Error during cleanup: {cleanup_error}")
        except Exception as e:
            logger.error(f"Server failed: {e}")
            raise
        finally:
            logger.info("Server shutdown complete")


def main():
    """Main entry point for the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Luxshare MCP Server")
    parser.add_argument("--config", help="Path to configuration file")
    parser.add_argument("--host", help="Host to bind to")
    parser.add_argument("--port", type=int, help="Port to bind to")
    parser.add_argument("--log-level", help="Log level")
    
    args = parser.parse_args()
    
    server = SimpleFastMCP("Luxshare MCP Server", config_path=args.config)
    server.run(
        host=args.host,
        port=args.port,
        log_level=args.log_level
    )


if __name__ == "__main__":
    main()