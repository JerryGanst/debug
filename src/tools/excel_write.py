import logging
from typing import Optional, List, Dict, Any
from ..core.file_manager import get_safe_filename
from ..utils.chart import create_chart_in_sheet as create_chart_impl
from ..utils.pivot import create_pivot_table as create_pivot_table_impl
from ..utils.tables import create_excel_table as create_table_impl
from ..utils.data import write_data
from ..utils.validation import validate_formula_in_cell_operation as validate_formula_impl
from ..utils.calculations import apply_formula as apply_formula_impl, CalculationError
from ..utils.formatting import format_range as format_range_func
from ..utils.sheet import (
    copy_range_operation,
    delete_range_operation,
    copy_sheet,
    delete_sheet,
    rename_sheet,
    merge_range,
    unmerge_range,
    insert_row,
    insert_cols,
    delete_rows,
    delete_cols,
)
from ..utils.workbook import create_workbook as create_workbook_impl, create_sheet
from ..utils.exceptions import (
    ChartError,
    PivotError,
    DataError,
    ValidationError,
    FormattingError,
    SheetError,
    WorkbookError,
)

logger = logging.getLogger("excel-mcp")

def register_excel_write_tools(mcp_server):
    """Register all Excel write tools with the MCP server."""

    # Advanced data tools
    @mcp_server.tool(tags={"excel", "write"})
    def create_chart(
        user_id: str,
        filename: str,
        sheet_name: str,
        data_range: str,
        chart_type: str,
        target_cell: str,
        title: str = "",
        x_axis: str = "",
        y_axis: str = ""
    ) -> str:
        """
        Create a chart in the Excel worksheet.
        
        Args:
            user_id (str): User ID for file organization
            filename (str): Name of the Excel file
            sheet_name (str): Name of worksheet
            data_range (str): Range of data to chart (e.g., 'A1:C10')
            chart_type (str): Type of chart (e.g., 'line', 'bar', 'column', 'pie')
            target_cell (str): Position to place chart (e.g., 'E2')
            title (str, optional): Title for the chart. Defaults to "".
            x_axis (str, optional): X-axis title. Defaults to "".
            y_axis (str, optional): Y-axis title. Defaults to "".
            
        Returns:
            str: Success message with filename
        """
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
            with mcp_server.file_manager.lock_file(file_path):
                result = create_chart_impl(
                    filepath=str(file_path),
                    sheet_name=sheet_name,
                    data_range=data_range,
                    chart_type=chart_type,
                    target_cell=target_cell,
                    title=title,
                    x_axis=x_axis,
                    y_axis=y_axis
                )
                safe_result = result["message"].replace(str(file_path), safe_filename)
                return safe_result
        except (ValidationError, ChartError) as e:
            safe_error = str(e).replace(str(file_path), safe_filename)
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error creating chart: {e}")
            raise

    @mcp_server.tool(tags={"excel", "write"})
    def create_pivot_table(
        user_id: str,
        filename: str,
        sheet_name: str,
        data_range: str,
        rows: List[str],
        values: List[str],
        columns: Optional[List[str]] = None,
        agg_func: str = "sum"
    ) -> str:
        """
        Create a pivot table from data range.
        
        Args:
            user_id (str): User ID for file organization
            filename (str): Name of the Excel file
            sheet_name (str): Source worksheet name
            data_range (str): Data range for pivot table (e.g., 'A1:D100')
            rows (List[str]): List of field names for row area
            values (List[str]): List of field names for values area
            columns (Optional[List[str]], optional): List of field names for column area. Defaults to None.
            agg_func (str, optional): Aggregation function (sum, count, average, max, min). Defaults to "sum".
            
        Returns:
            str: Success message with filename
        """
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
            with mcp_server.file_manager.lock_file(file_path):
                result = create_pivot_table_impl(
                    filepath=str(file_path),
                    sheet_name=sheet_name,
                    data_range=data_range,
                    rows=rows,
                    values=values,
                    columns=columns or [],
                    agg_func=agg_func
                )
                safe_result = result["message"].replace(str(file_path), safe_filename)
                return safe_result
        except (PivotError, ValidationError) as e:
            safe_error = str(e).replace(str(file_path), safe_filename)
            return f"Pivot Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error creating pivot table: {e}")
            raise

    @mcp_server.tool(tags={"excel", "write"})
    def create_table(
        user_id: str,
        filename: str,
        sheet_name: str,
        data_range: str,
        table_name: Optional[str] = None,
        table_style: str = "TableStyleMedium9"
    ) -> str:
        """
        Create an Excel table from a data range.
        
        Args:
            user_id (str): User ID for file organization
            filename (str): Name of the Excel file
            sheet_name (str): Name of worksheet
            data_range (str): Range to convert to table (e.g., 'A1:D10')
            table_name (Optional[str], optional): Name for the table. Defaults to None.
            table_style (str, optional): Table's style. Defaults to "TableStyleMedium9".
            
        Returns:
            str: Success message with filename
        """
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
            with mcp_server.file_manager.lock_file(file_path):
                result = create_table_impl(
                    filepath=str(file_path),
                    sheet_name=sheet_name,
                    data_range=data_range,
                    table_name=table_name,
                    table_style=table_style
                )
                safe_result = result["message"].replace(str(file_path), safe_filename)
                return safe_result
        except DataError as e:
            safe_error = str(e).replace(str(file_path), safe_filename)
            return f"Data Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            raise

    # Data related tools
    @mcp_server.tool(tags={"excel", "write"})
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
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
            with mcp_server.file_manager.lock_file(file_path):
                result = write_data(str(file_path), sheet_name, data, start_cell)
                safe_result = result["message"].replace(str(file_path), safe_filename)
                return safe_result
        except (ValidationError, DataError) as e:
            safe_error = str(e).replace(str(file_path), safe_filename)
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error writing data: {e}")
            raise

    @mcp_server.tool(tags={"excel", "write"})
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
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
            with mcp_server.file_manager.lock_file(file_path):
                validation = validate_formula_impl(str(file_path), sheet_name, cell, formula)
                if isinstance(validation, dict) and "error" in validation:
                    safe_error = validation["error"].replace(str(file_path), safe_filename)
                    return f"Error: {safe_error}"
                # then apply the formula
                result = apply_formula_impl(str(file_path), sheet_name, cell, formula)
                safe_result = result["message"].replace(str(file_path), safe_filename)
                return safe_result
        except (ValidationError, CalculationError) as e:
            safe_error = str(e).replace(str(file_path), safe_filename)
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error applying formula: {e}")
            raise

# Formatting tools

    @mcp_server.tool(tags={"excel", "write"})
    def format_range(
        user_id: str,
        filename: str,
        sheet_name: str,
        start_cell: str,
        end_cell: Optional[str] = None,
        bold: bool = False,
        italic: bool = False,
        underline: bool = False,
        font_size: Optional[int] = None,
        font_color: Optional[str] = None,
        bg_color: Optional[str] = None,
        border_style: Optional[str] = None,
        border_color: Optional[str] = None,
        number_format: Optional[str] = None,
        alignment: Optional[str] = None,
        wrap_text: bool = False,
        merge_cells: bool = False,
        protection: Optional[Dict[str, Any]] = None,
        conditional_format: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Format a range of cells with various styling options.
        
        Args:
            user_id (str): User ID for file organization
            filename (str): Name of the Excel file
            sheet_name (str): Name of worksheet
            start_cell (str): Start cell of the range (e.g., 'A1')
            end_cell (Optional[str], optional): End cell of the range (e.g., 'C10'). Defaults to None.
            bold (bool, optional): Whether text should be bold. Defaults to False.
            italic (bool, optional): Whether text should be italic. Defaults to False.
            underline (bool, optional): Whether text should be underlined. Defaults to False.
            font_size (Optional[int], optional): Font size (e.g., 12). Defaults to None.
            font_color (Optional[str], optional): Font color (hex or name). Defaults to None.
            bg_color (Optional[str], optional): Background color (hex or name). Defaults to None.
            border_style (Optional[str], optional): Border style (e.g., 'thin', 'medium', 'thick'). Defaults to None.
            border_color (Optional[str], optional): Border color (hex or name). Defaults to None.
            number_format (Optional[str], optional): Number format string. Defaults to None.
            alignment (Optional[str], optional): Text alignment. Defaults to None.
            wrap_text (bool, optional): Whether text should wrap. Defaults to False.
            merge_cells (bool, optional): Whether to merge cells. Defaults to False.
            protection (Optional[Dict[str, Any]], optional): Cell protection settings. Defaults to None.
            conditional_format (Optional[Dict[str, Any]], optional): Conditional formatting rules. Defaults to None.
            
        Returns:
            str: Success message with filename
        """
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
            with mcp_server.file_manager.lock_file(file_path):
                result = format_range_func(
                    filepath=str(file_path),
                    sheet_name=sheet_name,
                    start_cell=start_cell,
                    end_cell=end_cell,  # This can be None
                    bold=bold,
                    italic=italic,
                    underline=underline,
                    font_size=font_size,  # This can be None
                    font_color=font_color,  # This can be None
                    bg_color=bg_color,  # This can be None
                    border_style=border_style,  # This can be None
                    border_color=border_color,  # This can be None
                    number_format=number_format,  # This can be None
                    alignment=alignment,  # This can be None
                    wrap_text=wrap_text,
                    merge_cells=merge_cells,
                    protection=protection,  # This can be None
                    conditional_format=conditional_format  # This can be None
                )
                safe_result = result["message"].replace(str(file_path), f"'{safe_filename}'")
                return safe_result
        except (ValidationError, FormattingError) as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error formatting range: {e}")
            raise
               
    @mcp_server.tool(tags={"excel", "write"})
    def copy_range(
        user_id: str,
        filename: str,
        sheet_name: str,
        source_start: str,
        source_end: str,
        target_start: str,
        target_sheet: Optional[str] = None
    ) -> str:
        """
        Copy a range of cells to another location.
        
        Args:
            user_id (str): User ID for file organization
            filename (str): Name of the Excel file
            sheet_name (str): Name of worksheet
            source_start (str): Starting cell of source range (e.g., "A1")
            source_end (str): Ending cell of source range (e.g., "C3")
            target_start (str): Starting cell of target location (e.g., "E1")
            target_sheet (Optional[str], optional): Name of target worksheet. 
                If not provided, uses the source sheet. Defaults to None.
                
        Returns:
            str: Success message with filename
        """
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
            with mcp_server.file_manager.lock_file(file_path):
                result = copy_range_operation(
                    filepath = str(file_path),
                    sheet_name = sheet_name,
                    source_start = source_start,
                    source_end = source_end,
                    target_start = target_start,
                    target_sheet = target_sheet or sheet_name  # Use source sheet if target_sheet is None
                )
                safe_result = result["message"].replace(str(file_path), f"'{safe_filename}'")
                return safe_result
        except (ValidationError, SheetError) as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error copying range: {e}")
            raise
               
    @mcp_server.tool(tags={"excel", "write"})
    def delete_range(
        user_id: str,
        filename: str,
        sheet_name: str,
        start_cell: str,
        end_cell: str,
        shift_direction: str = "up"
    ) -> str:
        """
        Delete a range of cells and shift remaining cells.
        
        Args:
            user_id (str): User ID for file organization
            filename (str): Name of the Excel file
            sheet_name (str): Name of worksheet
            start_cell (str): Starting cell of range to delete (e.g., "A1")
            end_cell (str): Ending cell of range to delete (e.g., "C3")
            shift_direction (str, optional): Direction to shift remaining cells. 
                Valid values are "up", "left", "none". Defaults to "up".
                
        Returns:
            str: Success message with filename
        """
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
            with mcp_server.file_manager.lock_file(file_path):
                result = delete_range_operation(
                    filepath=str(file_path),
                    sheet_name=sheet_name,
                    start_cell=start_cell,
                    end_cell=end_cell,
                    shift_direction=shift_direction
                )
                safe_result = result["message"].replace(str(file_path), f"'{safe_filename}'")
                return safe_result
        except (ValidationError, SheetError) as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error deleting range: {e}")
            raise
        
    # Sheet related tools
    @mcp_server.tool(tags={"excel", "write"})
    def copy_worksheet(user_id: str, filename: str, source_sheet: str, target_sheet: str) -> str:
        """
        Copy a worksheet within the same workbook.
        
        Args:
            user_id (str): User ID for file organization. This parameter is required.
            filename (str): Name of the Excel file. This parameter is required.
            source_sheet (str): Name of source worksheet to copy. This parameter is required.
            target_sheet (str): Name for the new copied worksheet. This parameter is required.
            
        Returns:
            str: Success message with filename.
        """
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
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
        
    @mcp_server.tool(tags={"excel", "write"})
    def delete_worksheet(user_id: str, filename: str, sheet_name: str) -> str:
        """
        Delete a worksheet from the workbook.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of worksheet to delete
            
        Returns:
            str: Success message with filename
        """
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
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

    @mcp_server.tool(tags={"excel", "write"})
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
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
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
        
    @mcp_server.tool(tags={"excel", "write"})
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
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
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
        
    @mcp_server.tool(tags={"excel", "write"})
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
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
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

    @mcp_server.tool(tags={"excel", "write"})
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
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
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

    @mcp_server.tool(tags={"excel", "write"})
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
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
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

    @mcp_server.tool(tags={"excel", "write"})
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
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
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
        
    @mcp_server.tool(tags={"excel", "write"})
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
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
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
        
    # Workbook related tools
    @mcp_server.tool(tags={"excel", "write"})
    def create_workbook(user_id: str, filename: str) -> str:
        """
        Create a new Excel workbook.
        
        Args:
            user_id: User ID for file organization
            filename: Name of the workbook file to create
        Returns:
            Success message with the created filename
        """
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
            with mcp_server.file_manager.lock_file(file_path):
                # Create new workbook
                result = create_workbook_impl(str(file_path))
                logger.info(f"Created workbook: {safe_filename} for user {user_id}")
                safe_result = result["message"].replace(str(file_path), f"'{safe_filename}'")
                return safe_result
        except WorkbookError as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error creating workbook: {e}")
            raise

    @mcp_server.tool(tags={"excel", "write"})
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
        safe_filename = get_safe_filename(filename)
        file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
        try:
            with mcp_server.file_manager.lock_file(file_path):
                    result = create_sheet(str(file_path), sheet_name)
                    logger.info(f"Created worksheet '{sheet_name}' in {safe_filename} for user {user_id}")
                    safe_result = result["message"].replace(sheet_name, f"'{sheet_name}'")
                    return safe_result
        except (ValidationError, WorkbookError) as e:
            safe_error = str(e).replace(str(file_path), f"'{safe_filename}'")
            return f"Error: {safe_error}"
        except Exception as e:
            logger.error(f"Error creating worksheet: {e}")
            raise