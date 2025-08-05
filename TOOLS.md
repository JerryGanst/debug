# Excel MCP Server 2.0 - Tools Documentation

This document provides comprehensive information about all available tools in the Excel MCP Server 2.0 with tag-based filtering.

## 🏷️ Tag-Based Tool Access

**NEW in v2.0**: Tools are now filtered based on agent type. Different agents see different subsets of tools based on their permissions and functional requirements.

### Agent Profiles

| Agent Type | Description | Tool Count | Access Level |
|------------|-------------|------------|--------------|
| `excel_analyst` | Read-only data analysis | 6 | Data reading only |
| `excel_editor` | Full Excel editing | 22 | Complete Excel manipulation |
| `minio_reader` | Cloud storage read access | 3 | MinIO file listing/downloading |
| `minio_manager` | Cloud storage management | 3 | Full MinIO operations |
| `data_scientist` | Advanced analytics | 22 | Charts, pivots, data analysis |
| `report_generator` | Report creation | 22 | Formatting, charts, data |
| `admin` | Full system access | 25 | All available tools |

## 📋 Tool Categories

### 🏷️ Tags Legend
- **Domain**: `excel`, `minio`
- **Permission**: `read`, `write`, `delete`, `admin`
- **Resource**: `workbook`, `sheet`, `data`, `chart`, `pivot`, `format`, `storage`
- **Scope**: `user_scoped`, `global`, `shared`

---

## 📊 Workbook Operations

### create_workbook
**Tags**: `excel`, `write`, `workbook`, `file`, `user_scoped`  
**Access**: excel_editor, data_scientist, report_generator, admin

Creates a new Excel workbook.

```python
create_workbook(user_id: str, filename: str) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the workbook file to create (filename only, not full path)
- **Returns**: Success message with created filename

**Example Response**: `"Workbook 'report.xlsx' created successfully"`

---

### create_worksheet
**Tags**: `excel`, `write`, `sheet`, `workbook`, `user_scoped`  
**Access**: excel_editor, data_scientist, report_generator, admin

Creates a new worksheet in an existing workbook.

```python
create_worksheet(user_id: str, filename: str, sheet_name: str) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the workbook file (filename only)
- `sheet_name`: Name for the new worksheet
- **Returns**: Success message

**Example Response**: `"Worksheet 'Data' created successfully in 'report.xlsx'"`

---

### get_workbook_metadata
**Tags**: `excel`, `read`, `workbook`, `user_scoped`  
**Access**: excel_analyst, excel_editor, data_scientist, report_generator, admin

Get metadata about workbook including sheets and ranges.

```python
get_workbook_metadata(user_id: str, filename: str, include_ranges: bool = False) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the workbook file (filename only)
- `include_ranges`: Whether to include detailed range information
- **Returns**: JSON string with workbook metadata

---

## 📝 Data Operations

### read_data_from_excel
**Tags**: `excel`, `read`, `data`, `cell`, `user_scoped`  
**Access**: excel_analyst, excel_editor, data_scientist, report_generator, admin

Read data from Excel worksheet with cell metadata including validation rules.

```python
read_data_from_excel(
    user_id: str,
    filename: str,
    sheet_name: str,
    start_cell: str = "A1",
    end_cell: Optional[str] = None,
    preview_only: bool = False
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of Excel file (filename only)
- `sheet_name`: Name of worksheet
- `start_cell`: Starting cell (default A1)
- `end_cell`: Ending cell (optional, auto-expands if not provided)
- `preview_only`: Whether to return preview only
- **Returns**: JSON string containing structured cell data with validation metadata

**Example Response**: JSON with cell addresses, values, and validation info

---

### write_data_to_excel
**Tags**: `excel`, `write`, `data`, `cell`, `user_scoped`  
**Access**: excel_editor, data_scientist, report_generator, admin

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
- `filename`: Name of Excel file (filename only)
- `sheet_name`: Name of worksheet to write to
- `data`: List of lists containing data to write (sublists are rows)
- `start_cell`: Cell to start writing to, default is "A1"
- **Returns**: Success message with filename

**Example Response**: `"Data written successfully to 'report.xlsx' sheet 'Data'"`

---

### apply_formula
**Tags**: `excel`, `write`, `cell`, `user_scoped`  
**Access**: excel_editor, data_scientist, report_generator, admin

Apply Excel formula to cell.

```python
apply_formula(
    user_id: str,
    filename: str,
    sheet_name: str,
    cell: str,
    formula: str
) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of Excel file (filename only)
- `sheet_name`: Name of worksheet
- `cell`: Target cell address (e.g., 'A1')
- `formula`: Excel formula to apply
- **Returns**: Success message with filename

**Example Response**: `"Formula applied successfully to cell A1 in 'report.xlsx'"`

---

## 📋 Sheet Operations

### copy_worksheet
**Tags**: `excel`, `write`, `sheet`, `user_scoped`  
**Access**: excel_editor, data_scientist, report_generator, admin

Copy a worksheet within the same workbook.

```python
copy_worksheet(user_id: str, filename: str, source_sheet: str, target_sheet: str) -> str
```

---

### delete_worksheet
**Tags**: `excel`, `delete`, `sheet`, `user_scoped`  
**Access**: excel_editor, admin

Delete a worksheet from the workbook.

```python
delete_worksheet(user_id: str, filename: str, sheet_name: str) -> str
```

---

### rename_worksheet
**Tags**: `excel`, `write`, `sheet`, `user_scoped`  
**Access**: excel_editor, data_scientist, report_generator, admin

Rename a worksheet in the workbook.

```python
rename_worksheet(user_id: str, filename: str, old_name: str, new_name: str) -> str
```

---

### merge_cells
**Tags**: `excel`, `write`, `cell`, `user_scoped`  
**Access**: excel_editor, report_generator, admin

Merge a range of cells in the worksheet.

```python
merge_cells(user_id: str, filename: str, sheet_name: str, start_cell: str, end_cell: str) -> str

```

- `range_address`: Range to merge (e.g., 'A1:C3')

---

### unmerge_cells
**Tags**: `excel`, `write`, `cell`, `user_scoped`  
**Access**: excel_editor, report_generator, admin

Unmerge a range of cells in the worksheet.

```python
unmerge_cells(user_id: str, filename: str, sheet_name: str, start_cell: str, end_cell: str) -> str
```

---

### get_merged_cell_ranges
**Tags**: `excel`, `read`, `cell`, `user_scoped`  
**Access**: excel_analyst, excel_editor, data_scientist, report_generator, admin

Get all merged cell ranges in the worksheet.

```python
get_merged_cell_ranges(user_id: str, filename: str, sheet_name: str) -> str
```

- **Returns**: JSON string with merged ranges information

---

### insert_rows
**Tags**: `excel`, `write`, `sheet`, `user_scoped`  
**Access**: excel_editor, data_scientist, report_generator, admin

Insert one or more rows starting at the specified row.

```python
insert_rows(user_id: str, filename: str, sheet_name: str, start_row: int, count: int = 1) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file (filename only)
- `sheet_name`: Name of the worksheet
- `start_row`: Row number where insertion begins (1-based)
- `count`: Number of rows to insert (default: 1)
- **Returns**: Success message with operation details

**Example Response**: `"Inserted 2 row(s) starting at row 3 in sheet 'Data' of 'report.xlsx'"`

---

### insert_columns
**Tags**: `excel`, `write`, `sheet`, `user_scoped`  
**Access**: excel_editor, data_scientist, report_generator, admin

Insert one or more columns starting at the specified column.

```python
insert_columns(user_id: str, filename: str, sheet_name: str, start_col: int, count: int = 1) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file (filename only)
- `sheet_name`: Name of the worksheet
- `start_col`: Column number where insertion begins (1-based)
- `count`: Number of columns to insert (default: 1)
- **Returns**: Success message with operation details

**Example Response**: `"Inserted 1 column(s) starting at column 2 in sheet 'Data' of 'report.xlsx'"`

---

### delete_sheet_rows
**Tags**: `excel`, `delete`, `sheet`, `user_scoped`  
**Access**: excel_editor, data_scientist, report_generator, admin

Delete one or more rows starting at the specified row.

```python
delete_sheet_rows(user_id: str, filename: str, sheet_name: str, start_row: int, count: int = 1) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file (filename only)
- `sheet_name`: Name of the worksheet
- `start_row`: Row number where deletion begins (1-based)
- `count`: Number of rows to delete (default: 1)
- **Returns**: Success message with operation details

**Example Response**: `"Deleted 3 row(s) starting at row 5 in sheet 'Data' of 'report.xlsx'"`

---

### delete_sheet_columns
**Tags**: `excel`, `delete`, `sheet`, `user_scoped`  
**Access**: excel_editor, data_scientist, report_generator, admin

Delete one or more columns starting at the specified column.

```python
delete_sheet_columns(user_id: str, filename: str, sheet_name: str, start_col: int, count: int = 1) -> str
```

- `user_id`: User ID for file organization
- `filename`: Name of the Excel file (filename only)
- `sheet_name`: Name of the worksheet
- `start_col`: Column number where deletion begins (1-based)
- `count`: Number of columns to delete (default: 1)
- **Returns**: Success message with operation details

**Example Response**: `"Deleted 2 column(s) starting at column 3 in sheet 'Data' of 'report.xlsx'"`

---

## 🎨 Formatting & Validation

### format_range
**Tags**: `excel`, `write`, `format`, `cell`, `user_scoped`  
**Access**: excel_editor, report_generator, admin

Format a range of cells with various styling options.

```python
format_range(
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
) -> str
```

- `range_address`: Range to format (e.g., 'A1:C10')
- Supports font properties, colors, borders, number formats, alignment, and conditional formatting

---

### apply_data_validation
**Tags**: `excel`, `write`, `validation`, `cell`, `user_scoped`  
**Access**: excel_editor, data_scientist, admin

Apply data validation to a range of cells.

```python
apply_data_validation(
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
) -> str
```

- `validation_type`: Type of validation ('list', 'whole', 'decimal', etc.)

---

### get_validation_info
**Tags**: `excel`, `read`, `validation`, `user_scoped`  
**Access**: excel_analyst, excel_editor, data_scientist, admin

Get validation information for all cells in a worksheet.

```python
get_validation_info(user_id: str, filename: str, sheet_name: str) -> str
```

- **Returns**: JSON string with validation information

---

## 📊 Advanced Features

### create_chart
**Tags**: `excel`, `write`, `chart`, `user_scoped`  
**Access**: data_scientist, report_generator, admin

Create a chart in the Excel worksheet.

```python
create_chart(
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
```

- `chart_type`: Type of chart ('line', 'bar', 'column', 'pie')
- `data_range`: Range of data to chart (e.g., 'A1:C10')

---

### create_pivot_table_tool
**Tags**: `excel`, `write`, `pivot`, `user_scoped`  
**Access**: data_scientist, admin

Create a pivot table from data range.

```python
create_pivot_table_tool(
    user_id: str,
    filename: str,
    sheet_name: str,
    data_range: str,
    rows: List[str],
    values: List[str],
    columns: Optional[List[str]] = None,
    agg_func: str = "sum"
) -> str
```

- `rows`: List of field names for row area
- `values`: List of field names for values area
- `agg_func`: Aggregation function (sum, count, average, max, min)

---

### create_table
**Tags**: `excel`, `write`, `data`, `user_scoped`  
**Access**: excel_editor, data_scientist, report_generator, admin

Create an Excel table from a data range.

```python
create_table(
    user_id: str,
    filename: str,
    sheet_name: str,
    data_range: str,
    table_name: str,
    has_headers: bool = True
) -> str
```

---

## ☁️ MinIO Cloud Storage

### list_minio_files
**Tags**: `minio`, `read`, `storage`, `file`, `user_scoped`  
**Access**: minio_reader, minio_manager, admin

List all files in the MinIO bucket for a specific user.

```python
list_minio_files(user_id: str) -> List[Dict[str, Any]]
```

- **Returns**: List of file information dictionaries with filename, size, and last_modified

**Example Response**:
```json
[
    {
        "filename": "report.xlsx",
        "size": 12345,
        "last_modified": "2025-01-01T10:00:00"
    }
]
```

---

### pull_minio_file
**Tags**: `minio`, `read`, `storage`, `file`, `user_scoped`  
**Access**: minio_reader, minio_manager, admin

Download a file from MinIO to the local Excel directory.

```python
pull_minio_file(user_id: str, filename: str) -> str
```

- `filename`: Name of the file in MinIO (filename only)
- **Returns**: Success message with filename

**Example Response**: `"File 'report.xlsx' downloaded successfully from MinIO"`

---

### push_minio_file
**Tags**: `minio`, `write`, `storage`, `file`, `user_scoped`  
**Access**: minio_manager, admin

Upload a local Excel file to MinIO, then remove the local copy.

```python
push_minio_file(user_id: str, filename: str) -> str
```

- `filename`: Name of the local file to upload (filename only)
- **Returns**: Success message with uploaded filename

**Note**: The uploaded file gets a "(mod)" suffix to differentiate from originals.

**Example Response**: `"File uploaded to MinIO as 'report(mod).xlsx'"`

---

## 🔧 Agent Management

### list_available_tools_for_agent
**Tags**: No filtering (system tool)  
**Access**: All agents

List tools available to a specific agent type.

```python
list_available_tools_for_agent(agent_type: str = None) -> str
```

- `agent_type`: Type of agent ('excel_analyst', 'excel_editor', etc.)
- **Returns**: JSON string with available tools for the agent

---

### get_agent_profiles
**Tags**: No filtering (system tool)  
**Access**: All agents

Get list of available predefined agent profiles.

```python
get_agent_profiles() -> str
```

- **Returns**: JSON string with available agent profiles and their requirements

---

## 🚨 Important Changes in v2.0

### ⚠️ Breaking Changes

1. **Filename Returns**: All tools now return filenames instead of full file paths
   - **Before**: `"File saved to /excel_files/user_123/report.xlsx"`
   - **After**: `"File saved to 'report.xlsx'"`

2. **Agent-based Access**: Tools are filtered based on agent type
   - Specify agent type when connecting: `--agent-type excel_analyst`
   - Different agents see different subsets of tools

3. **Parameter Names**: Some parameters have been standardized
   - Use `filename` parameter for file names (not `file_name`)
   - Parameters always expect filenames, not full paths

### 🔄 Migration Guide

#### For MCP Clients
1. Handle filename-only returns in tool responses
2. Specify appropriate agent type for your use case
3. Update error handling for new response patterns

#### Example Usage
```bash
# Start server with specific agent type
python3 server.py --agent-type excel_analyst

# Excel analyst can only read data
read_data_from_excel(user_id="123", filename="report.xlsx", sheet_name="Data")

# Excel editor can manipulate files
create_workbook(user_id="123", filename="new_report.xlsx")
write_data_to_excel(user_id="123", filename="new_report.xlsx", ...)
```

---

## 📊 Tool Access Matrix

| Tool Category | excel_analyst | excel_editor | minio_reader | minio_manager | data_scientist | report_generator | admin |
|---------------|---------------|--------------|--------------|---------------|----------------|------------------|-------|
| **Read Data** | ✅ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Write Data** | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Workbook Ops** | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Sheet Ops** | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Formatting** | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Charts** | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Pivot Tables** | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **MinIO List** | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ |
| **MinIO Read** | ❌ | ❌ | ✅ | ✅ | ❌ | ❌ | ✅ |
| **MinIO Write** | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ |
| **Row/Col Insert** | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |
| **Row/Col Delete** | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ | ✅ |

---

## 🛡️ Security Features

- **File Locking**: Automatic protection against concurrent access
- **User Isolation**: Each user has their own file directory
- **Path Sanitization**: Prevents directory traversal attacks
- **Agent Permissions**: Tools filtered based on agent capabilities
- **Safe Returns**: Only filenames returned, never full paths

---

For more information about the server architecture and setup, see [README.md](README.md) and [CHANGELOG.md](CHANGELOG.md).