"""
Advanced Excel tools (charts, pivot tables, tables) for Excel MCP server.
"""

import logging
from typing import Optional, List, Dict, Any
from ..core.tag_system import ToolTags
from ..core.file_manager import get_safe_filename
from ..utils.chart import create_chart_in_sheet as create_chart_impl
from ..utils.pivot import create_pivot_table as create_pivot_table_impl
from ..utils.tables import create_excel_table as create_table_impl
from ..utils.exceptions import ChartError, PivotError, DataError

logger = logging.getLogger("excel-mcp")


def register_advanced_tools(mcp_server):
    """Register all advanced Excel tools with the MCP server."""
    
    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["chart"],
            scopes=["user_scoped"]
        )
    )
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
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of worksheet
            chart_type: Type of chart (e.g., 'line', 'bar', 'column', 'pie')
            data_range: Range of data to chart (e.g., 'A1:C10')
            chart_title: Optional title for the chart
            x_axis_title: Optional X-axis title
            y_axis_title: Optional Y-axis title
            position: Position to place chart (default: 'E2')
            
        Returns:
            Success message with filename
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
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
                return result['message']
        except (ValidationError, ChartError) as e:
            return f"Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error creating chart: {e}")
            raise ChartError(f"Failed to create chart: {str(e)}")

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["pivot"],
            scopes=["user_scoped"]
        )
    )
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
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Source worksheet name
            data_range: Data range for pivot table (e.g., 'A1:D100')
            rows: List of field names for row area
            values: List of field names for values area
            columns: List of field names for column area (optional)
            agg_func: Aggregation function (sum, count, average, max, min)
            
        Returns:
            Success message with filename
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
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
                return result["message"]
                
        except PivotError as e:
            return f"Pivot Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error creating pivot table: {e}")
            raise PivotError(f"Failed to create pivot table: {str(e)}")

    @mcp_server.tool(
        tags=ToolTags(
            functional_domains=["excel"],
            permissions=["write"],
            resource_types=["data"],
            scopes=["user_scoped"]
        )
    )
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
            user_id: User ID for file organization
            filename: Name of the Excel file
            sheet_name: Name of worksheet
            data_range: Range to convert to table (e.g., 'A1:D10')
            table_name: Name for the table
            table_style: Table's style
            
        Returns:
            Success message with filename
        """
        try:
            safe_filename = get_safe_filename(filename)
            file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
            
            with mcp_server.file_manager.lock_file(file_path):
                result = create_table_impl(
                    filepath=str(file_path),
                    sheet_name=sheet_name,
                    data_range=data_range,
                    table_name=table_name,
                    table_style=table_style
                )
                return result["message"]
           
        except DataError as e:
            return f"Data Error: {str(e)}"
        except Exception as e:
            logger.error(f"Error creating table: {e}")
            raise DataError(f"Failed to create table: {str(e)}")