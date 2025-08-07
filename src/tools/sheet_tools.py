"""
Sheet management tools for Excel MCP server.
"""

import logging
from ..core.tag_system import ToolTags
from ..core.file_manager import get_safe_filename
from ..utils.sheet import (
    copy_sheet, 
    delete_sheet, 
    rename_sheet, 
    merge_range, 
    unmerge_range, 
    get_merged_ranges, 
    insert_row, 
    insert_cols, 
    delete_rows,
    delete_cols
)
from ..utils.exceptions import SheetError, ValidationError

logger = logging.getLogger("excel-mcp")


def register_sheet_tools(mcp_server):
    """Register all sheet-related tools with the MCP server."""
    
    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["sheet"],
            scopes=["user_scoped"]
        )
    )
    def copy_worksheet(user_id: str, filename: str, source_sheet: str, target_sheet: str) -> str:
        """
        Copy a worksheet within the same workbook.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            source_sheet: Name of source worksheet to copy
            target_sheet: Name for the new copied worksheet
            
        Returns:
            Success message with filename
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            with mcp_server.file_manager.lock_file(file_path):
                result = copy_sheet(str(file_path), source_sheet, target_sheet)
                safe_result = result["message"].replace(str(file_path), f"'{safe_filename}'")
                return safe_result
        except (ValidationError, SheetError) as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error copying worksheet: {e}")
            raise

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["delete"],
            resource_types=["sheet"],
            scopes=["user_scoped"]
        )
    )
    def delete_worksheet(user_id: str, filename: str, sheet_name: str) -> str:
        """
        Delete a worksheet from the workbook.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of worksheet to delete
            
        Returns:
            Success message with filename
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            with mcp_server.file_manager.lock_file(file_path):
                result = delete_sheet(str(file_path), sheet_name)
                safe_result = result["message"].replace(str(file_path), f"'{safe_filename}'")
                return safe_result
        except (ValidationError, SheetError) as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error deleting worksheet: {e}")
            raise

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["sheet"],
            scopes=["user_scoped"]
        )
    )
    def rename_worksheet(user_id: str, filename: str, old_name: str, new_name: str) -> str:
        """
        Rename a worksheet in the workbook.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            old_name: Current name of worksheet
            new_name: New name for worksheet
            
        Returns:
            Success message with filename
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            with mcp_server.file_manager.lock_file(file_path):
                result = rename_sheet(str(file_path), old_name, new_name)
                safe_result = result["message"].replace(str(file_path), f"'{safe_filename}'")
                return safe_result
        except (ValidationError, SheetError) as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error renaming worksheet: {e}")
            raise

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["cell"],
            scopes=["user_scoped"]
        )
    )
    def merge_cells(user_id: str, filename: str, sheet_name: str, start_cell: str, end_cell: str) -> str:
        """
        Merge a range of cells in the worksheet.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of worksheet
            range_address: Range to merge (e.g., 'A1:C3')
            
        Returns:
            Success message with filename
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            with mcp_server.file_manager.lock_file(file_path):
                result = merge_range(str(file_path), sheet_name, start_cell, end_cell)
                safe_result = result["message"].replace(str(file_path), f"'{safe_filename}'")
                return safe_result
        except (ValidationError, SheetError) as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error merging cells: {e}")
            raise

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["cell"],
            scopes=["user_scoped"]
        )
    )
    def unmerge_cells(user_id: str, filename: str, sheet_name: str, start_cell: str, end_cell: str) -> str:
        """
        Unmerge a range of cells in the worksheet.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of worksheet
            range_address: Range to unmerge (e.g., 'A1:C3')
            
        Returns:
            Success message with filename
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            with mcp_server.file_manager.lock_file(file_path):
                result = unmerge_range(str(file_path), sheet_name, start_cell, end_cell)
                safe_result = result["message"].replace(str(file_path), f"'{safe_filename}'")
                return safe_result
        except (ValidationError, SheetError) as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error unmerging cells: {e}")
            raise

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["read"],
            resource_types=["cell"],
            scopes=["user_scoped"]
        )
    )
    def get_merged_cells(user_id: str, filename: str, sheet_name: str) -> str:
        """
        Get all merged cell ranges in the worksheet.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of worksheet
            
        Returns:
            JSON string with merged ranges information
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            with mcp_server.file_manager.lock_file(file_path):
                result = str(get_merged_ranges(str(file_path), sheet_name))
                safe_result = result.replace(str(file_path), f"'{safe_filename}'")
                return safe_result
        except (ValidationError, SheetError) as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error getting merged cells: {e}")
            raise


    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["sheet"],
            scopes=["user_scoped"]
        )
    )
    def insert_rows(user_id: str, filename: str, sheet_name: str, start_row: int, count: int = 1) -> str:
        """
        Insert one or more rows starting at the specified row.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of the worksheet
            start_row: Row number where insertion begins (1-based)
            count: Number of rows to insert (default: 1)
            
        Returns:
            Success message with operation details
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            with mcp_server.file_manager.lock_file(file_path):
                result = insert_row(str(file_path), sheet_name, start_row, count)
                safe_result = result["message"].replace(str(file_path), f"'{safe_filename}'")
                return safe_result
        except (ValidationError, SheetError) as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error inserting rows: {e}") 
            raise

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["sheet"],
            scopes=["user_scoped"]
        )
    )
    def insert_columns(user_id: str, filename: str, sheet_name: str, start_col: int, count: int = 1) -> str:
        """
        Insert one or more columns starting at the specified column.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of the worksheet
            start_col: Column number where insertion begins (1-based)
            count: Number of columns to insert (default: 1)
            
        Returns:
            Success message with operation details
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            with mcp_server.file_manager.lock_file(file_path):
                result = insert_cols(str(file_path), sheet_name, start_col, count)
                safe_result = result["message"].replace(str(file_path), f"'{safe_filename}'")
                return safe_result
        except (ValidationError, SheetError) as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error inserting columns: {e}") 
            raise

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["delete"],
            resource_types=["sheet"],
            scopes=["user_scoped"]
        )
    )
    def delete_sheet_rows(user_id: str, filename: str, sheet_name: str, start_row: int, count: int = 1) -> str:
        """
        Delete one or more rows starting at the specified row.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of the worksheet
            start_row: Row number where deletion begins (1-based)
            count: Number of rows to delete (default: 1)
            
        Returns:
            Success message with operation details
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            with mcp_server.file_manager.lock_file(file_path):
                result = delete_rows(str(file_path), sheet_name, start_row, count)
                safe_result = result["message"].replace(str(file_path), f"'{safe_filename}'")
                return safe_result
        except (ValidationError, SheetError) as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error deleting rows: {e}") 
            raise

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["delete"],
            resource_types=["sheet"],
            scopes=["user_scoped"]
        )
    )
    def delete_sheet_columns(user_id: str, filename: str, sheet_name: str, start_col: int, count: int = 1) -> str:
        """
        Delete one or more columns starting at the specified column.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of the worksheet
            start_col: Column number where deletion begins (1-based)
            count: Number of columns to delete (default: 1)
            
        Returns:
            Success message with operation details
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            with mcp_server.file_manager.lock_file(file_path):
                result = delete_cols(str(file_path), sheet_name, start_col, count)
                safe_result = result["message"].replace(str(file_path), f"'{safe_filename}'")
                return safe_result
        except (ValidationError, SheetError) as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error deleting columns: {e}")
            raise
