"""
MinIO storage tools for Excel MCP server.
"""

import logging
from typing import List, Dict, Any
from minio import Minio
from minio.error import S3Error
from ..core.tag_system import ToolTags
from ..core.file_manager import get_safe_filename
from ..utils.exceptions import DataError

logger = logging.getLogger("excel-mcp")


def _get_minio_client(config):
    """Helper function to create MinIO client."""
    return Minio(
        config.minio.endpoint.replace("http://", "").replace("https://", ""),
        access_key=config.minio.access_key,
        secret_key=config.minio.secret_key,
        secure=False,
    )


def register_minio_tools(mcp_server):
    """Register all MinIO-related tools with the MCP server."""
    
    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["minio"],
            permissions=["read"],
            resource_types=["storage", "file"],
            scopes=["user_scoped"]
        )
    )
    def list_minio_files(user_id: str) -> List[Dict[str, Any]]:
        """
        List all files in the MinIO bucket for a specific user.
        
        Args:
            user_id: User ID for accessing user-specific files
            
        Returns:
            List of file information dictionaries with name, size, and last_modified
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
            
            return file_list
            
        except Exception as e:
            logger.error(f"Error listing MinIO files: {e}")
            raise DataError(f"Failed to list MinIO files: {str(e)}")

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["minio"],
            permissions=["read"],
            resource_types=["storage", "file"],
            scopes=["user_scoped"]
        )
    )
    def pull_minio_file(user_id: str, filename: str) -> str:
        """
        Download a file from MinIO to the local Excel directory.

        Args:
            user_id: User ID for accessing user-specific files
            filename: Name of the file in MinIO
            
        Returns:
            Success message with filename (not full path)
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
                
                result = {"message": f"File '{safe_filename}' downloaded successfully from MinIO"}
                return result["message"]
                
        except S3Error as e:
            logger.error(f"Error pulling file from MinIO: {e}")
            raise DataError(f"Failed to pull file from MinIO: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error pulling file: {e}")
            raise DataError(f"Failed to pull file: {str(e)}")

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["minio"],
            permissions=["write"],
            resource_types=["storage", "file"],
            scopes=["user_scoped"]
        )
    )
    def push_minio_file(user_id: str, filename: str) -> str:
        """
        Upload a local Excel file to MinIO, then remove the local copy.
        The uploaded file gets a "(mod)" suffix to differentiate from originals.

        Args:
            user_id: User ID for accessing user-specific files
            filename: Name of the local file to upload
            
        Returns:
            Success message with the uploaded filename
        """
        try:
            safe_filename = get_safe_filename(filename)
            client = _get_minio_client(mcp_server.config)
            bucket_name = mcp_server.config.minio.bucket
            
            # Define local file path
            local_file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
            if not local_file_path.is_file():
                raise FileNotFoundError(f"File not found: {safe_filename}")
            
            # Create modified file name with (mod) extension
            file_stem = local_file_path.stem
            file_suffix = local_file_path.suffix
            modified_filename = f"{file_stem}(mod){file_suffix}"
            object_name = f"private/{user_id}/{modified_filename}"
            
            with mcp_server.file_manager.lock_file(local_file_path):
                try:
                    # Upload the file to MinIO
                    client.fput_object(bucket_name, object_name, str(local_file_path))
                    logger.info(f"Successfully pushed file {safe_filename} to MinIO as {modified_filename}")
                    
                    # Remove the local file after successful upload
                    local_file_path.unlink()
                    logger.info(f"Removed local file: {safe_filename}")
                    
                    result = {"message": f"File uploaded to MinIO as '{modified_filename}'"}
                    return result["message"]
                    
                except S3Error as e:
                    logger.error(f"Error pushing file to MinIO: {e}")
                    raise DataError(f"Failed to upload file to MinIO: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error in push_minio_file: {e}")
            raise DataError(f"Failed to push file: {str(e)}")