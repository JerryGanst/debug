"""
Formatting and validation tools for Excel MCP server.
"""

import logging
from typing import Optional, Dict, Any
from ..core.tag_system import ToolTags
from ..core.file_manager import get_safe_filename
from ..utils.formatting import format_range as format_range_util
from ..utils.validation import validate_range_in_sheet_operation
from ..utils.cell_validation import get_all_validation_ranges
from ..utils.exceptions import FormattingError, ValidationError

logger = logging.getLogger("excel-mcp")


def register_format_tools(mcp_server):
    """Register all formatting and validation tools with the MCP server."""
    
    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["format", "cell"],
            scopes=["user_scoped"]
        )
    )
    def format_range(
        user_id: str,
        filename: str,
        sheet_name: str,
        range_address: str,
        font_name: Optional[str] = None,
        font_size: Optional[int] = None,
        bold: Optional[bool] = None,
        italic: Optional[bool] = None,
        font_color: Optional[str] = None,
        background_color: Optional[str] = None,
        border: Optional[str] = None,
        number_format: Optional[str] = None,
        alignment: Optional[str] = None,
        protection: Optional[Dict[str, Any]] = None,
        conditional_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format a range of cells with various styling options.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of worksheet
            range_address: Range to format (e.g., 'A1:C10')
            font_name: Font name (e.g., 'Arial')
            font_size: Font size (e.g., 12)
            bold: Whether text should be bold
            italic: Whether text should be italic
            font_color: Font color (hex or name)
            background_color: Background color (hex or name)
            border: Border style
            number_format: Number format string
            alignment: Text alignment
            protection: Cell protection settings
            conditional_format: Conditional formatting rules
            
        Returns:
            Success message with filename
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
            with mcp_server.file_manager.lock_file(file_path):
                # Parse range to get start and end cells
                if ':' in range_address:
                    start_cell, end_cell = range_address.split(':')
                else:
                    start_cell, end_cell = range_address, None
                
                format_range_util(
                    filepath=str(file_path),
                    sheet_name=sheet_name,
                    start_cell=start_cell,
                    end_cell=end_cell,
                    font_size=font_size,
                    bold=bold,
                    italic=italic,
                    font_color=font_color,
                    bg_color=background_color,
                    number_format=number_format,
                    alignment=alignment,
                    protection=protection,
                    conditional_format=conditional_format
                )
                
                return f"Range {range_address} formatted successfully in sheet '{sheet_name}' of '{safe_filename}'"
                
        except (ValidationError, FormattingError) as e:
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error formatting range: {e}")
            raise FormattingError(f"Failed to format range: {str(e)}")

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["validation", "cell"],
            scopes=["user_scoped"]
        )
    )
    def apply_data_validation(
        user_id: str,
        filename: str,
        sheet_name: str,
        range_address: str,
        validation_type: str,
        formula1: Optional[str] = None,
        formula2: Optional[str] = None,
        allow_blank: bool = True,
        input_title: Optional[str] = None,
        input_message: Optional[str] = None,
        error_title: Optional[str] = None,
        error_message: Optional[str] = None,
        show_input_message: bool = True,
        show_error_message: bool = True
    ) -> str:
        """
        Apply data validation to a range of cells.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of worksheet
            range_address: Range to validate (e.g., 'A1:A10')
            validation_type: Type of validation ('list', 'whole', 'decimal', etc.)
            formula1: First validation formula/value
            formula2: Second validation formula/value (for ranges)
            allow_blank: Whether to allow blank values
            input_title: Title for input message
            input_message: Input message text
            error_title: Title for error message
            error_message: Error message text
            show_input_message: Whether to show input message
            show_error_message: Whether to show error message
            
        Returns:
            Success message with filename
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
            with mcp_server.file_manager.lock_file(file_path):
                validate_range_in_sheet_operation(
                    file_path=str(file_path),
                    sheet_name=sheet_name,
                    range_address=range_address,
                    validation_type=validation_type,
                    formula1=formula1,
                    formula2=formula2,
                    allow_blank=allow_blank,
                    input_title=input_title,
                    input_message=input_message,
                    error_title=error_title,
                    error_message=error_message,
                    show_input_message=show_input_message,
                    show_error_message=show_error_message
                )
                
                return f"Data validation applied to range {range_address} in sheet '{sheet_name}' of '{safe_filename}'"
                
        except ValidationError as e:
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error applying validation: {e}")
            raise ValidationError(f"Failed to apply validation: {str(e)}")

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["read"],
            resource_types=["validation"],
            scopes=["user_scoped"]
        )
    )
    def get_validation_info(user_id: str, filename: str, sheet_name: str) -> str:
        """
        Get validation information for all cells in a worksheet.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of worksheet
            
        Returns:
            JSON string with validation information
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
            with mcp_server.file_manager.lock_file(file_path):
                from openpyxl import load_workbook
                wb = load_workbook(str(file_path))
                ws = wb[sheet_name]
                validations = get_all_validation_ranges(ws)
                
                import json
                return json.dumps({
                    "filename": safe_filename,
                    "sheet_name": sheet_name,
                    "validation_rules": validations
                }, indent=2, default=str)
                
        except Exception as e:
            logger.error(f"Error getting validation info: {e}")
            raise ValidationError(f"Failed to get validation info: {str(e)}")