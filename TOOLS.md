# Excel MCP Server Tools

This document provides detailed information about all available tools in the Excel MCP server.

## MinIO Storage Operations

### list_minio_files

List all files in the MinIO bucket for a specific user.

```python
list_minio_files(user_id: str) -> List[Dict[str, Any]]
```

- `user_id`: User ID for accessing user-specific files.
- Returns: A list of dictionaries containing file information. Each dictionary has the following keys:
  - `filename` (str): The name of the file
  - `size` (int): The size of the file in bytes
  - `last_modified` (str, optional): The last modified timestamp in ISO format

### pull_minio_file

Download a file from MinIO to the local Excel directory.

```python
pull_minio_file(user_id: str, filename: str) -> str
```

- `user_id`: User ID for accessing user-specific files.
- `filename`: Name of the file in MinIO.
- Returns: Success message with the filename

### push_minio_file

Upload a local Excel file to MinIO, then remove the local copy. The uploaded file gets a unique name to differentiate from originals.

```python
push_minio_file(user_id: str, filename: str) -> str
```

- `user_id`: User ID for accessing user-specific files.
- `filename`: Name of the local file to upload.
- Returns: A dictionary containing a success message with the uploaded filename.

## Workbook Operations

### create_workbook

Create a new Excel workbook.

```python
create_workbook(user_id: str, filename: str) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the workbook file to create
- Returns: Success message with the created filename

### create_worksheet

Create a new worksheet in an existing workbook.

```python
create_worksheet(user_id: str, filename: str, sheet_name: str) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the workbook file
- `sheet_name`: Name for the new worksheet
- Returns: Success message with the created sheet name

### get_workbook_metadata

Get metadata about workbook including sheets and ranges.

```python
get_workbook_metadata(user_id: str, filename: str, include_ranges: bool = False) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the workbook file
- `include_ranges`: Whether to include range information, default to false
- Returns: JSON string with workbook metadata

## Data Operations

### write_data_to_excel

Write data to Excel worksheet.

```python
write_data_to_excel(
    user_id: str, 
    filename: str,
    sheet_name: str,
    data: List[List],
    start_cell: str = "A1"
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Name of worksheet to write to
- `data`: List of lists containing data to write (sublists are rows)
- `start_cell`: Cell to start writing to, default is "A1"
- Returns: Success message with filename

### read_data_from_excel

Read data from Excel worksheet with cell metadata including validation rules.

```python
read_data_from_excel(
    user_id: str, 
    filename: str,
    sheet_name: str,
    start_cell: str,
    end_cell: str,
    preview_only: bool = False
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Name of worksheet
- `start_cell`: Starting cell (e.g., 'A1')
- `end_cell`: Ending cell (e.g., 'C10')
- `preview_only`: Whether to return preview only
- Returns: JSON string containing structured cell data with validation metadata. Each cell includes: address, value, row, column, and validation info (if any).

## Formatting Operations

### format_range

Format a range of cells with various styling options.

```python
format_range(
    user_id: str, filename: str,
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
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Name of worksheet
- `start_cell`: Start cell of the range (e.g., 'A1')
- `end_cell`: End cell of the range (e.g., 'C10'). Defaults to None.
- `bold`: Whether text should be bold. Defaults to False.
- `italic`: Whether text should be italic. Defaults to False.
- `underline`: Whether text should be underlined. Defaults to False.
- `font_size`: Font size (e.g., 12). Defaults to None.
- `font_color`: Font color (hex or name). Defaults to None.
- `bg_color`: Background color (hex or name). Defaults to None.
- `border_style`: Border style (e.g., 'thin', 'medium', 'thick'). Defaults to None.
- `border_color`: Border color (hex or name). Defaults to None.
- `number_format`: Number format string. Defaults to None.
- `alignment`: Text alignment. Defaults to None.
- `wrap_text`: Whether text should wrap. Defaults to False.
- `merge_cells`: Whether to merge cells. Defaults to False.
- `protection`: Cell protection settings. Defaults to None.
- `conditional_format`: Conditional formatting rules. Defaults to None.
- Returns: Success message with filename

### merge_cells

Merge cells in a specified range.

```python
merge_cells(
    user_id: str, 
    filename: str,
    sheet_name: str,
    start_cell: str,
    end_cell: str
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Name of worksheet
- `start_cell`: Start cell of the range (e.g., 'A1')
- `end_cell`: End cell of the range (e.g., 'C10')
- Returns: Success message with filename

### unmerge_cells

Unmerge cells in a specified range.

```python
unmerge_cells(
    user_id: str, 
    filename: str,
    sheet_name: str,
    start_cell: str,
    end_cell: str
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Name of worksheet
- `start_cell`: Start cell of the range (e.g., 'A1')
- `end_cell`: End cell of the range (e.g., 'C10')
- Returns: Success message with filename

### get_merged_cells

Get all merged cell ranges in the worksheet.

```python
get_merged_cells(user_id: str, filename: str, sheet_name: str) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Name of worksheet
- Returns: String with merged ranges information


## Formula Operations

### apply_formula

Apply Excel formula to a specific cell.

```python
apply_formula(user_id: str, filename: str, sheet_name: str, cell: str, formula: str) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Name of worksheet
- `cell`: Target cell reference (e.g., 'A1')
- `formula`: Excel formula to apply (e.g., '=SUM(A1:A10)')
- Returns: Success message with filename

### validate_formula_syntax

Validate Excel formula syntax without applying it to a cell.

```python
validate_formula_syntax(user_id: str, filename: str, sheet_name: str, cell: str, formula: str) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Name of worksheet
- `cell`: Target cell reference (e.g., 'A1')
- `formula`: Excel formula to validate (e.g., '=SUM(A1:A10)')
- Returns: Validation result message

## Chart Operations

### create_chart

Create a chart in a worksheet with customizable options.

```python
create_chart(
    user_id: str, filename: str,
    sheet_name: str,
    data_range: str,
    chart_type: str,
    target_cell: str,
    title: str = "",
    x_axis: str = "",
    y_axis: str = ""
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Name of worksheet
- `data_range`: Range containing chart data (e.g., 'A1:B10')
- `chart_type`: Type of chart (line, bar, pie, scatter, area)
- `target_cell`: Cell where to place chart (e.g., 'D1')
- `title`: Optional chart title
- `x_axis`: Optional X-axis label
- `y_axis`: Optional Y-axis label
- Returns: Success message with filename

## Pivot Table Operations

### create_pivot_table

Create a pivot table in a worksheet with customizable options.

```python
create_pivot_table(
    user_id: str, filename: str,
    sheet_name: str,
    data_range: str,
    rows: List[str],
    values: List[str],
    columns: Optional[List[str]] = None,
    agg_func: str = "sum"
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Name of worksheet
- `data_range`: Range containing source data (e.g., 'A1:D50')
- `rows`: Fields for row labels (e.g., ['Region', 'Product'])
- `values`: Fields for values (e.g., ['Sales', 'Quantity'])
- `columns`: Optional fields for column labels (e.g., ['Year'])
- `agg_func`: Aggregation function (sum, count, average, max, min)
- Returns: Success message with filename

## Table Operations

### create_table

Creates a native Excel table from a specified range of data with optional styling.

```python
create_table(
    user_id: str, filename: str,
    sheet_name: str,
    data_range: str,
    table_name: Optional[str] = None,
    table_style: str = "TableStyleMedium9"
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Name of worksheet
- `data_range`: The cell range for the table (e.g., "A1:D5")
- `table_name`: Optional unique name for the table
- `table_style`: Optional visual style for the table (e.g., "TableStyleLight1")
- Returns: Success message with filename

## Worksheet Operations

### copy_worksheet

Copy a worksheet within the same workbook.

```python
copy_worksheet(user_id: str, filename: str, source_sheet: str, target_sheet: str) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `source_sheet`: Name of sheet to copy
- `target_sheet`: Name for new sheet
- Returns: Success message with filename

### delete_worksheet

Delete a worksheet from a workbook.

```python
delete_worksheet(user_id: str, filename: str, sheet_name: str) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Name of sheet to delete
- Returns: Success message with filename

### rename_worksheet

Rename a worksheet in a workbook.

```python
rename_worksheet(user_id: str, filename: str, old_name: str, new_name: str) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `old_name`: Current sheet name
- `new_name`: New sheet name
- Returns: Success message with filename

## Range Operations

### copy_range

Copy a range of cells to another location.

```python
copy_range(
    user_id: str, filename: str,
    sheet_name: str,
    source_start: str,
    source_end: str,
    target_start: str,
    target_sheet: Optional[str] = None
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Source worksheet name
- `source_start`: Starting cell of source range (e.g., 'A1')
- `source_end`: Ending cell of source range (e.g., 'C10')
- `target_start`: Starting cell for paste (e.g., 'E1')
- `target_sheet`: Optional target worksheet name
- Returns: Success message with filename

### delete_range

Delete a range of cells and shift remaining cells accordingly.

```python
delete_range(
    user_id: str, filename: str,
    sheet_name: str,
    start_cell: str,
    end_cell: str,
    shift_direction: str = "up"
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Target worksheet name
- `start_cell`: Starting cell of range (e.g., 'A1')
- `end_cell`: Ending cell of range (e.g., 'C10')
- `shift_direction`: Direction to shift cells ("up", "left", or "none")
- Returns: Success message with filename

### validate_excel_range

Validate if a range exists and is properly formatted in a worksheet.

```python
validate_excel_range(
    user_id: str, filename: str,
    sheet_name: str,
    start_cell: str,
    end_cell: str
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Target worksheet name
- `start_cell`: Starting cell of range (e.g., 'A1')
- `end_cell`: Ending cell of range (e.g., 'C3')
- Returns: Success message with filename

### get_data_validation_info

Get all data validation rules in a worksheet.

This tool helps identify which cell ranges have validation rules 
and what types of validation are applied.

```python
get_data_validation_info(user_id: str, filename: str, sheet_name: str) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Name of worksheet
- Returns: JSON string containing all validation rules in the worksheet

## Row and Column Operations

### insert_rows

Insert one or more rows starting at the specified row.

```python
insert_rows(
    user_id: str, filename: str,
    sheet_name: str,
    start_row: int,
    count: int = 1
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Target worksheet name
- `start_row`: Row number where to start inserting (1-based)
- `count`: Number of rows to insert (default: 1)
- Returns: Success message with filename

### insert_columns

Insert one or more columns starting at the specified column.

```python
insert_columns(
    user_id: str, filename: str,
    sheet_name: str,
    start_col: int,
    count: int = 1
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Target worksheet name
- `start_col`: Column number where to start inserting (1-based)
- `count`: Number of columns to insert (default: 1)
- Returns: Success message with filename

### delete_sheet_rows

Delete one or more rows starting at the specified row.

```python
delete_sheet_rows(
    user_id: str, filename: str,
    sheet_name: str,
    start_row: int,
    count: int = 1
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Target worksheet name
- `start_row`: Row number where to start deleting (1-based)
- `count`: Number of rows to delete (default: 1)
- Returns: Success message with filename

### delete_sheet_columns

Delete one or more columns starting at the specified column.

```python
delete_sheet_columns(
    user_id: str, filename: str,
    sheet_name: str,
    start_col: int,
    count: int = 1
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file
- `sheet_name`: Target worksheet name
- `start_col`: Column number where to start deleting (1-based)
- `count`: Number of columns to delete (default: 1)
- Returns: Success message with filename

## Tool Categories

The tools are organized into the following categories based on their functionality:

- **MinIO Storage Operations**: File management in cloud storage
- **Workbook Operations**: Creating and managing Excel workbooks
- **Data Operations**: Reading and writing data to worksheets
- **Formatting Operations**: Cell styling and formatting
- **Formula Operations**: Excel formula management
- **Chart Operations**: Creating charts and graphs
- **Pivot Table Operations**: Data analysis and summarization
- **Table Operations**: Creating structured Excel tables
- **Worksheet Operations**: Managing individual worksheets
- **Range Operations**: Working with cell ranges
- **Row and Column Operations**: Inserting and deleting rows/columns

Each tool includes proper error handling and returns user-friendly messages with the filename (not full paths) for security and usability.

**Note**: The `read_data_from_excel` tool automatically includes validation metadata for individual cells when available.