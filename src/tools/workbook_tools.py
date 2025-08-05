"""
Workbook management tools for Excel MCP server.
"""

import logging
from ..core.tag_system import ToolTags
from ..core.file_manager import get_safe_filename
from ..utils.workbook import get_workbook_info
from ..utils.exceptions import WorkbookError, ValidationError
from ..utils.workbook import create_workbook as create_workbook_impl
from ..utils.workbook import create_sheet

logger = logging.getLogger("excel-mcp")


def register_workbook_tools(mcp_server):
    """Register all workbook-related tools with the MCP server."""
    
    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["workbook", "file"],
            scopes=["user_scoped"]
        )
    )
    def create_workbook(user_id: str, filename: str) -> str:
        """
        Create a new Excel workbook.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the workbook file to create
            
        Returns:
            Success message with the created filename
        """
        try:
            # Ensure we only work with safe filenames
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
            with mcp_server.file_manager.lock_file(file_path):
                # Create new workbook
                result = create_workbook_impl(str(file_path))
                
                logger.info(f"Created workbook: {safe_filename} for user {user_id}")
                return result["message"].replace(str(file_path), f"'{safe_filename}'")
                
                
        except Exception as e:
            logger.error(f"Error creating workbook: {e}")
            raise WorkbookError(f"Failed to create workbook: {str(e)}")
    
    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["sheet", "workbook"],
            scopes=["user_scoped"]
        )
    )
    def create_worksheet(user_id: str, filename: str, sheet_name: str) -> str:
        """
        Create a new worksheet in an existing workbook.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the workbook file
            sheet_name: Name for the new worksheet
            
        Returns:
            Success message with the created sheet name
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
            with mcp_server.file_manager.lock_file(file_path):
                from ..utils.workbook import create_sheet
                try:
                    result = create_sheet(str(file_path), sheet_name)
                    logger.info(f"Created worksheet '{sheet_name}' in {safe_filename} for user {user_id}")
                    return result["message"].replace(sheet_name, f"'{sheet_name}'") + f" in '{safe_filename}'"
                except WorkbookError as e:
                    if "already exists" in str(e):
                        return f"Error: Sheet '{sheet_name}' already exists"
                    raise
        except Exception as e:
            logger.error(f"Error creating worksheet: {e}")
            raise WorkbookError(f"Failed to create worksheet: {str(e)}")
    
    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["read"],
            resource_types=["workbook"],
            scopes=["user_scoped"]
        )
    )
    def get_workbook_metadata(
        user_id: str, 
        filename: str, 
        include_ranges: bool = False
    ) -> str:
        """
        Get metadata about workbook including sheets and ranges.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the workbook file
            include_ranges: Whether to include range information
            
        Returns:
            JSON string with workbook metadata
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
            # Use shared lock for read operation
            with mcp_server.file_manager.lock_file(file_path):
                result = get_workbook_info(str(file_path), include_ranges=include_ranges)
                return str(result)
        except WorkbookError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error getting workbook metadata: {e}")
            raise