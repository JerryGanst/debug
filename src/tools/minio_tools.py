"""
MinIO storage tools for Excel MCP server.
"""

import logging
import json
from typing import List, Dict, Any
from minio import Minio
from minio.error import S3Error
from ..core.file_manager import get_safe_filename
from ..utils.exceptions import DataError
from fastmcp.exceptions import ToolError

logger = logging.getLogger("excel-mcp")


def _get_minio_client(config):
    """Helper function to create MinIO client."""
    # Respect scheme and explicit secure flag from config
    endpoint = (
        config.minio.endpoint.replace("http://", "").replace("https://", "")
        if isinstance(config.minio.endpoint, str) else config.minio.endpoint
    )
    return Minio(
        endpoint,
        access_key=config.minio.access_key,
        secret_key=config.minio.secret_key,
        secure=bool(getattr(config.minio, "secure", False)),
    )


def _get_unique_filename(client, bucket_name, user_id, base_filename):
    """Generate a unique filename by checking existing files in MinIO."""
    # First check if the base filename exists
    prefix = f"private/{user_id}/{base_filename}"
    objects = list(client.list_objects(bucket_name, prefix=prefix, recursive=False))
    
    # If base filename doesn't exist, return it as is
    if not objects:
        return base_filename
    
    # If base filename exists, try numbered versions
    file_stem = base_filename
    file_suffix = ""
    
    # Separate file extension if it exists
    if "." in base_filename:
        file_parts = base_filename.rsplit(".", 1)
        file_stem = file_parts[0]
        file_suffix = f".{file_parts[1]}"
    
    # Try numbered versions starting from 1
    counter = 1
    while True:
        new_filename = f"{file_stem}({counter}){file_suffix}"
        prefix = f"private/{user_id}/{new_filename}"
        objects = list(client.list_objects(bucket_name, prefix=prefix, recursive=False))
    
        # If this filename doesn't exist, return it
        if not objects:
            return new_filename
    
        counter += 1
        # Safety check to prevent infinite loops
        if counter > 1000:
            raise ToolError("Unable to generate unique filename after 1000 attempts.")


def register_minio_tools(mcp_server):
    """Register all MinIO-related tools with the MCP server."""
    
    @mcp_server.tool(tags={"minio", "read"})
    def list_minio_files(user_id: str) -> str:
        """
        List all files in the MinIO bucket for a specific user.
        
        Args:
            user_id (str): User ID for accessing user-specific files. This parameter is required.
            
        Returns:
            str: JSON string of file info objects. Each object contains:
            - filename (str)
            - size (int)
            - last_modified (str | null)
        """
        try:
            client = _get_minio_client(mcp_server.config)
            bucket_name = mcp_server.config.minio.bucket
            prefix = f"private/{user_id}/"
            
            objects = client.list_objects(bucket_name, prefix=prefix, recursive=True)
            file_list = []
            
            for obj in objects:
                # Extract just the filename from the object path
                filename = obj.object_name.split('/')[-1]
                file_info = {
                    "filename": filename,  # Return only filename to avoid path confusion
                    "size": obj.size,
                    "last_modified": obj.last_modified.isoformat() if obj.last_modified else None
                }
                file_list.append(file_info)
                logger.info(f"Found file: {filename} for user {user_id}")
            return json.dumps(file_list, indent=2, default=str)
        except S3Error as e:
            logger.error(f"Error listing MinIO files: {e}")
            raise ToolError("Failed to list files from storage.")
        except Exception as e:
            logger.error(f"Unexpected error listing MinIO files: {e}")
            raise ToolError("An unexpected error occurred while listing files.")

    @mcp_server.tool(tags={"minio", "read"})
    def pull_minio_file(user_id: str, filename: str) -> str:
        """
        Download a file from MinIO to the local Excel directory.

        Args:
            user_id (str): User ID for accessing user-specific files. This parameter is required.
            filename (str): Name of the file in MinIO. This parameter is required.
            
        Returns:
            str: Success message with the filename (not full path).
        """
        try:
            safe_filename = get_safe_filename(filename)
            client = _get_minio_client(mcp_server.config)
            bucket_name = mcp_server.config.minio.bucket
            
            # Define the object path in MinIO and local file path
            object_name = f"private/{user_id}/{safe_filename}"
            local_file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
            # Create local directory if it doesn't exist
            local_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with mcp_server.file_manager.lock_file(local_file_path):
                # Download the file from MinIO
                client.fget_object(bucket_name, object_name, str(local_file_path))
                logger.info(f"Successfully pulled file {safe_filename} from MinIO for user {user_id}")
                
                return f"File '{safe_filename}' downloaded successfully from MinIO"
                
        except S3Error as e:
            logger.error(f"Error pulling file from MinIO: {e}")
            raise ToolError("Failed to download file from storage.")
        except Exception as e:
            logger.error(f"Unexpected error pulling file: {e}")
            raise ToolError("An unexpected error occurred while downloading the file.")

    @mcp_server.tool(tags={"minio", "write"})
    def push_minio_file(user_id: str, filename: str) -> str:
        """
        Upload a local Excel file to MinIO, then remove the local copy.
        The uploaded file gets a unique name to differentiate from originals.

        Args:
            user_id (str): User ID for accessing user-specific files. This parameter is required.
            filename (str): Name of the local file to upload. This parameter is required.
            
        Returns:
            str: Success message with the uploaded filename.
        """
        try:
            safe_filename = get_safe_filename(filename)
            client = _get_minio_client(mcp_server.config)
            bucket_name = mcp_server.config.minio.bucket
            
            # Define local file path
            local_file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
            if not local_file_path.is_file():
                raise FileNotFoundError(f"File not found: {safe_filename}")
            
            # Generate a unique filename to avoid overwriting existing files
            base_filename = local_file_path.name
            unique_filename = _get_unique_filename(client, bucket_name, user_id, base_filename)
            object_name = f"private/{user_id}/{unique_filename}"
            
            with mcp_server.file_manager.lock_file(local_file_path):
                try:
                    # Upload the file to MinIO
                    client.fput_object(bucket_name, object_name, str(local_file_path))
                    logger.info(f"Successfully pushed file {safe_filename} to MinIO as {unique_filename}")
                    
                    # Remove the local file after successful upload
                    local_file_path.unlink()
                    logger.info(f"Removed local file: {safe_filename}")
                    
                    return f"File uploaded to MinIO as '{unique_filename}', local copy {safe_filename} has been removed"
                    
                except S3Error as e:
                    logger.error(f"Error pushing file to MinIO: {e}")
                    raise ToolError("Failed to upload file to storage.")
                
        except Exception as e:
            logger.error(f"Error in push_minio_file: {e}")
            raise ToolError("An unexpected error occurred while uploading the file.")