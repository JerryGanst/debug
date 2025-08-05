# Excel MCP Server Tools

This document provides detailed information about all available tools in the Excel MCP server.

## Important Note on User ID Parameter

**All tools now require a `user_id` parameter as the first argument.** This parameter is used to organize files by user in a multi-user environment. Files are stored in the structure: `/excel_files/<user_id>/<filename>`.

For example:
- User ID: `31005892`
- File: `transcript.xlsx`
- Full path: `/excel_files/31005892/transcript.xlsx`

## Workbook Operations

### create_workbook

Creates a new Excel workbook.

```python
create_workbook(user_id: str, filepath: str) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path where to create workbook (relative to user directory)
- Returns: Success message with created file path

### create_worksheet

Creates a new worksheet in an existing workbook.

```python
create_worksheet(user_id: str, filepath: str, sheet_name: str) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Name for the new worksheet
- Returns: Success message

### get_workbook_metadata

Get metadata about workbook including sheets and ranges.

```python
get_workbook_metadata(user_id: str, filepath: str, include_ranges: bool = False) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `include_ranges`: Whether to include range information
- Returns: String representation of workbook metadata

## Data Operations

### write_data_to_excel

Write data to Excel worksheet.

```python
write_data_to_excel(
    user_id: str,
    filepath: str,
    sheet_name: str,
    data: List[Dict],
    start_cell: str = "A1"
) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Target worksheet name
- `data`: List of dictionaries containing data to write
- `start_cell`: Starting cell (default: "A1")
- Returns: Success message

### read_data_from_excel

Read data from Excel worksheet.

```python
read_data_from_excel(
    user_id: str,
    filepath: str,
    sheet_name: str,
    start_cell: str = "A1",
    end_cell: str = None,
    preview_only: bool = False
) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Source worksheet name
- `start_cell`: Starting cell (default: "A1")
- `end_cell`: Optional ending cell
- `preview_only`: Whether to return only a preview
- Returns: String representation of data

## Formatting Operations

### format_range

Apply formatting to a range of cells.

```python
format_range(
    user_id: str,
    filepath: str,
    sheet_name: str,
    start_cell: str,
    end_cell: str = None,
    bold: bool = False,
    italic: bool = False,
    underline: bool = False,
    font_size: int = None,
    font_color: str = None,
    bg_color: str = None,
    border_style: str = None,
    border_color: str = None,
    number_format: str = None,
    alignment: str = None,
    wrap_text: bool = False,
    merge_cells: bool = False,
    protection: Dict[str, Any] = None,
    conditional_format: Dict[str, Any] = None
) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Target worksheet name
- `start_cell`: Starting cell of range
- `end_cell`: Optional ending cell of range
- Various formatting options (see parameters)
- Returns: Success message

### merge_cells

Merge a range of cells.

```python
merge_cells(user_id: str, filepath: str, sheet_name: str, start_cell: str, end_cell: str) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Target worksheet name
- `start_cell`: Starting cell of range
- `end_cell`: Ending cell of range
- Returns: Success message

### unmerge_cells

Unmerge a previously merged range of cells.

```python
unmerge_cells(user_id: str, filepath: str, sheet_name: str, start_cell: str, end_cell: str) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Target worksheet name
- `start_cell`: Starting cell of range
- `end_cell`: Ending cell of range
- Returns: Success message

### get_merged_cells

Get merged cells in a worksheet.

```python
get_merged_cells(user_id: str, filepath: str, sheet_name: str) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Target worksheet name
- Returns: String representation of merged cells


## Formula Operations

### apply_formula

Apply Excel formula to cell.

```python
apply_formula(user_id: str, filepath: str, sheet_name: str, cell: str, formula: str) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Target worksheet name
- `cell`: Target cell reference
- `formula`: Excel formula to apply
- Returns: Success message

### validate_formula_syntax

Validate Excel formula syntax without applying it.

```python
validate_formula_syntax(user_id: str, filepath: str, sheet_name: str, cell: str, formula: str) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Target worksheet name
- `cell`: Target cell reference
- `formula`: Excel formula to validate
- Returns: Validation result message

## Chart Operations

### create_chart

Create chart in worksheet.

```python
create_chart(
    user_id: str,
    filepath: str,
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
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Target worksheet name
- `data_range`: Range containing chart data
- `chart_type`: Type of chart (line, bar, pie, scatter, area)
- `target_cell`: Cell where to place chart
- `title`: Optional chart title
- `x_axis`: Optional X-axis label
- `y_axis`: Optional Y-axis label
- Returns: Success message

## Pivot Table Operations

### create_pivot_table

Create pivot table in worksheet.

```python
create_pivot_table(
    user_id: str,
    filepath: str,
    sheet_name: str,
    data_range: str,
    rows: List[str],
    values: List[str],
    columns: List[str] = None,
    agg_func: str = "sum"
) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Target worksheet name
- `data_range`: Range containing source data
- `target_cell`: Cell where to place pivot table
- `rows`: Fields for row labels
- `values`: Fields for values
- `columns`: Optional fields for column labels
- `agg_func`: Aggregation function (sum, count, average, max, min)
- Returns: Success message

## Table Operations

### create_table

Creates a native Excel table from a specified range of data.

> **New in 2024-07:** The tool now performs a workbook-wide check to guarantee that `table_name` is unique across *all* worksheets. If a duplicate is found, a `DataError` is raised before writing, preventing Excel corruption.

```python
create_table(
    user_id: str,
    filepath: str,
    sheet_name: str,
    data_range: str,
    table_name: str = None,
    table_style: str = "TableStyleMedium9"
) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to the Excel file (relative to user directory).
- `sheet_name`: Name of the worksheet.
- `data_range`: The cell range for the table (e.g., "A1:D5").
- `table_name`: Optional unique name for the table. Must be unique across the whole workbook.
- `table_style`: Optional visual style for the table.
- Returns: Success message.

## Worksheet Operations

### copy_worksheet

Copy worksheet within workbook.

```python
copy_worksheet(user_id: str, filepath: str, source_sheet: str, target_sheet: str) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `source_sheet`: Name of sheet to copy
- `target_sheet`: Name for new sheet
- Returns: Success message

### delete_worksheet

Delete worksheet from workbook.

```python
delete_worksheet(user_id: str, filepath: str, sheet_name: str) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Name of sheet to delete
- Returns: Success message

### rename_worksheet

Rename worksheet in workbook.

```python
rename_worksheet(user_id: str, filepath: str, old_name: str, new_name: str) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `old_name`: Current sheet name
- `new_name`: New sheet name
- Returns: Success message

## Range Operations

### copy_range

Copy a range of cells to another location.

```python
copy_range(
    user_id: str,
    filepath: str,
    sheet_name: str,
    source_start: str,
    source_end: str,
    target_start: str,
    target_sheet: str = None
) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Source worksheet name
- `source_start`: Starting cell of source range
- `source_end`: Ending cell of source range
- `target_start`: Starting cell for paste
- `target_sheet`: Optional target worksheet name
- Returns: Success message

### delete_range

Delete a range of cells and shift remaining cells.

```python
delete_range(
    user_id: str,
    filepath: str,
    sheet_name: str,
    start_cell: str,
    end_cell: str,
    shift_direction: str = "up"
) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Target worksheet name
- `start_cell`: Starting cell of range
- `end_cell`: Ending cell of range
- `shift_direction`: Direction to shift cells ("up" or "left")
- Returns: Success message

### validate_excel_range

Validate if a range exists and is properly formatted.

```python
validate_excel_range(
    user_id: str,
    filepath: str,
    sheet_name: str,
    start_cell: str,
    end_cell: str = None
) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Target worksheet name
- `start_cell`: Starting cell of range
- `end_cell`: Optional ending cell of range
- Returns: Validation result message

### get_data_validation_info

Get data validation rules and metadata for a worksheet.

```python
get_data_validation_info(user_id: str, filepath: str, sheet_name: str) -> str
```

- `user_id`: User ID for file organization
- `filepath`: Path to Excel file (relative to user directory)
- `sheet_name`: Target worksheet name
- Returns: JSON string containing all data validation rules with metadata including:
  - Validation type (list, whole, decimal, date, time, textLength)
  - Operator (between, notBetween, equal, greaterThan, lessThan, etc.)
  - Allowed values for list validations (resolved from ranges)
  - Formula constraints for numeric/date validations
  - Cell ranges where validation applies
  - Prompt and error messages

**Note**: The `read_data_from_excel` tool automatically includes validation metadata for individual cells when available.

## MinIO File Storage Tools

### list_minio_files

Lists all files stored in MinIO for a specific user.

**Parameters:**
- `user_id` (string, required): The user ID to list files for

**Returns:**
- A list of file objects containing:
  - `name`: The full object path in MinIO
  - `size`: File size in bytes
  - `last_modified`: ISO format timestamp of last modification

**Example:**
```json
{
  "user_id": "11450"
}
```

### pull_minio_file

Downloads a file from MinIO storage to the local file system.

**Parameters:**
- `user_id` (string, required): The user ID who owns the file
- `file_name` (string, required): The name of the file to download

**Returns:**
- The local file path where the file was saved

**Behavior:**
- Downloads from MinIO path: `<bucket>/private/<user_id>/<file_name>`
- Saves to local path: `<EXCEL_FILES_PATH>/<user_id>/<file_name>`
- Creates the local directory structure if it doesn't exist

**Example:**
```json
{
  "user_id": "11450",
  "file_name": "transcript.xlsx"
}
```

### push_minio_file

Uploads a local file to MinIO storage with a "(mod)" suffix and removes the local file.

**Parameters:**
- `user_id` (string, required): The user ID who owns the file
- `file_name` (string, required): The name of the file to upload

**Returns:**
- Success message with the MinIO object path

**Behavior:**
- Reads from local path: `<EXCEL_FILES_PATH>/<user_id>/<file_name>`
- Uploads to MinIO path: `<bucket>/private/<user_id>/<file_stem>(mod)<extension>`
- Deletes the local file after successful upload
- Example: `transcript.xlsx` becomes `transcript(mod).xlsx` in MinIO

**Example:**
```json
{
  "user_id": "11450",
  "file_name": "transcript.xlsx"
}
```