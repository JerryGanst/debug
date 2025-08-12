"""
Configuration management for the FastMCP Excel server.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class MCPConfig:
    """MCP Server configuration."""
    excel_files_path: str = "./excel_files"
    port: int = 3210
    host: str = "0.0.0.0"
    log_level: str = "info"


@dataclass  
class MinIOConfig:
    """MinIO storage configuration."""
    endpoint: str
    access_key: str
    secret_key: str
    bucket: str
    secure: bool = False


@dataclass
class ServerConfig:
    """Complete server configuration."""
    mcp: MCPConfig
    minio: MinIOConfig


def load_config(config_path: str = None) -> ServerConfig:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file, defaults to configs.yaml in project root
        
    Returns:
        ServerConfig instance with loaded configuration
    """
    if config_path is None:
        # Default to configs.yaml in project root
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "configs.yaml"
    
    with open(config_path, 'r') as f:
        config_data = yaml.safe_load(f)
    
    # Parse MCP config
    mcp_data = config_data.get('MCP_CONFIG', {})
    mcp_config = MCPConfig(
        excel_files_path=mcp_data.get('EXCEL_FILES_PATH', './excel_files'),
        port=mcp_data.get('PORT', 3210),
        host=mcp_data.get('HOST', '0.0.0.0'),
        log_level=mcp_data.get('LOG_LEVEL', 'info')
    )
    
    # Parse MinIO config
    minio_data = config_data.get('MINIO_CONFIG', {})
    endpoint_value = minio_data['MINIO_ENDPOINT']
    # Allow explicit flag; otherwise infer from endpoint scheme
    secure_flag = minio_data.get('MINIO_SECURE')
    if secure_flag is None:
        secure_flag = str(endpoint_value).startswith("https://")

    minio_config = MinIOConfig(
        endpoint=endpoint_value,
        access_key=minio_data['MINIO_ACCESS_KEY'],
        secret_key=minio_data['MINIO_SECRET_KEY'],
        bucket=minio_data['MINIO_BUCKET'],
        secure=bool(secure_flag)
    )
    
    return ServerConfig(mcp=mcp_config, minio=minio_config)