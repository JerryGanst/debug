"""
Data manipulation tools for Excel MCP server.
"""

import logging
from typing import List, Optional
from ..core.tag_system import ToolTags
from ..core.file_manager import get_safe_filename
from ..utils.data import read_excel_range_with_metadata, write_data
from ..utils.exceptions import DataError, ValidationError

logger = logging.getLogger("excel-mcp")


def register_data_tools(mcp_server):
    """Register all data-related tools with the MCP server."""
    
    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["read"],
            resource_types=["data", "cell"],
            scopes=["user_scoped"]
        )
    )
    def read_data_from_excel(
        user_id: str,
        filename: str,
        sheet_name: str,
        start_cell: str = "A1",
        end_cell: Optional[str] = None,
        preview_only: bool = False
    ) -> str:
        """
        Read data from Excel worksheet with cell metadata including validation rules.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of worksheet
            start_cell: Starting cell (default A1)
            end_cell: Ending cell (optional, auto-expands if not provided)
            preview_only: Whether to return preview only
        
        Returns:  
            JSON string containing structured cell data with validation metadata.
            Each cell includes: address, value, row, column, and validation info (if any).
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
            with mcp_server.file_manager.lock_file(file_path):
                result = read_excel_range_with_metadata(
                    str(file_path), 
                    sheet_name, 
                    start_cell, 
                    end_cell
                )
                
                if not result or not result.get("cells"):
                    return "No data found in specified range"
                
                # Ensure we return filename instead of full path
                if 'filename' not in result:
                    result['filename'] = safe_filename
                
                # Return as formatted JSON string
                import json
                return json.dumps(result, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error reading data: {e}")
            raise DataError(f"Failed to read data: {str(e)}")

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["data", "cell"],
            scopes=["user_scoped"]
        )
    )
    def write_data_to_excel(
        user_id: str,
        filename: str,
        sheet_name: str,
        data: List[List],
        start_cell: str = "A1",
    ) -> str:
        """
        Write data to Excel worksheet.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of worksheet to write to
            data: List of lists containing data to write (sublists are rows)
            start_cell: Cell to start writing to, default is "A1"
        
        Returns:
            Success message with filename
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
            with mcp_server.file_manager.lock_file(file_path):
                result = write_data(str(file_path), sheet_name, data, start_cell)
                
                # Return success message with filename only
                return f"Data written successfully to '{safe_filename}' sheet '{sheet_name}'"
                
        except (ValidationError, DataError) as e:
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error writing data: {e}")
            raise DataError(f"Failed to write data: {str(e)}")

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["cell"],
            scopes=["user_scoped"]
        )
    )
    def apply_formula(
        user_id: str,
        filename: str,
        sheet_name: str,
        cell: str,
        formula: str,
    ) -> str:
        """
        Apply Excel formula to cell.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of worksheet
            cell: Target cell address (e.g., 'A1')
            formula: Excel formula to apply
            
        Returns:
            Success message with filename
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
            with mcp_server.file_manager.lock_file(file_path):
                from ..utils.validation import validate_formula_in_cell_operation
                
                # Validate and apply formula
                result = validate_formula_in_cell_operation(
                    str(file_path), sheet_name, cell, formula
                )
                
                return f"Formula applied successfully to cell {cell} in '{safe_filename}'"
                
        except ValidationError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error applying formula: {e}")
            raise DataError(f"Failed to apply formula: {str(e)}")