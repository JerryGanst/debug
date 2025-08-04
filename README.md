# Excel MCP Server 2.0

A modern, tag-based Excel MCP (Model Context Protocol) server with agent-specific tool filtering, file locking, and standardized architecture.

## 🚀 Features

- **Tag-based Tool Filtering**: Different agents see only relevant tools based on their permissions and functional requirements
- **File Locking**: Concurrent access protection for multi-client scenarios
- **Standardized Architecture**: Clean separation of concerns with `src/` structure
- **Agent Profiles**: Predefined profiles for common use cases (analyst, editor, admin, etc.)
- **Path Safety**: Eliminates path confusion by returning only filenames
- **Row/Column Operations**: Insert and delete rows/columns with validation and bounds checking
- **MinIO Integration**: Cloud storage support with user isolation
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

## 🏗️ Architecture

```
src/
├── core/                    # Core server functionality
│   ├── config.py           # Configuration management
│   ├── file_manager.py     # File operations with locking
│   ├── mcp_server.py       # Tagged FastMCP server implementation
│   └── tag_system.py       # Tool tagging and agent profiles
├── tools/                   # MCP tool modules
│   ├── workbook_tools.py   # Workbook creation/management
│   ├── data_tools.py       # Data read/write operations
│   ├── sheet_tools.py      # Worksheet operations
│   ├── format_tools.py     # Formatting and validation
│   ├── advanced_tools.py   # Charts, pivot tables, tables
│   └── minio_tools.py      # Cloud storage operations
├── utils/                   # Utility modules (from original)
└── server.py               # Main server entry point
```

## 🏷️ Tag System

The server uses a multi-dimensional tag system for tool filtering:

### Tag Dimensions

1. **Functional Domain**: `excel`, `minio`, `knowledge_base`, `web_search`, `translation`
2. **Permission Level**: `read`, `write`, `delete`, `admin`
3. **Resource Type**: `file`, `data`, `chart`, `pivot`, `format`, `validation`, `workbook`, `sheet`, `cell`, `storage`
4. **Scope**: `user_scoped`, `global`, `shared`

### Predefined Agent Profiles

- **excel_analyst**: Read-only Excel data analysis - *6 tools* (`read`)
- **excel_editor**: Full Excel editing capabilities - *22 tools* (`excel`, `write`, `user_scoped`)
- **minio_reader**: Read-only cloud storage access - *3 tools* (`minio`, `read`)
- **minio_manager**: Full cloud storage management - *3 tools* (`minio`, `write`, `storage`, `user_scoped`)
- **data_scientist**: Advanced Excel analysis with charts/pivots - *22 tools* (`excel`, `data`, `chart`, `pivot`)
- **report_generator**: Report creation with formatting - *22 tools* (`excel`, `format`, `chart`)
- **admin**: Full access to all tools - *25 tools* (`admin`)

## 🚦 Starting the Server

### Basic Usage

```bash
# Run with default configuration
python3 -m src.server

# Run with specific agent profile
python3 -m src.server --agent-type excel_analyst

# Run with custom host/port
python3 -m src.server --host 0.0.0.0 --port 3210
```

### Configuration

All configuration is loaded from `configs.yaml`:

```yaml
MCP_CONFIG:
  EXCEL_FILES_PATH: ./excel_files
  PORT: 3210
  HOST: 0.0.0.0
  LOG_LEVEL: info

MINIO_CONFIG:
  MINIO_ENDPOINT: http://your-minio-server:9000
  MINIO_ACCESS_KEY: your-access-key
  MINIO_SECRET_KEY: your-secret-key
  MINIO_BUCKET: ai-file
```

## 📂 File Organization

Files are organized by user ID with automatic directory creation:
- Pattern: `/excel_files/<user_id>/<filename>`
- Example: `/excel_files/user_12345/report.xlsx`

## 🔒 Concurrent Access Protection

The server implements file locking to prevent conflicts:
- Automatic file locking during operations
- Configurable timeout (default: 30 seconds)
- Safe cleanup on operation completion or failure

## 🛠️ Tool Categories

### Workbook Tools
- `create_workbook`: Create new Excel workbooks
- `create_worksheet`: Add worksheets to existing workbooks
- `get_workbook_metadata`: Get workbook information

### Data Tools  
- `read_data_from_excel`: Read data with metadata
- `write_data_to_excel`: Write data to worksheets
- `apply_formula`: Apply Excel formulas to cells

### Sheet Tools
- `copy_worksheet`: Copy worksheets within workbooks
- `delete_worksheet`: Remove worksheets
- `rename_worksheet`: Rename worksheets
- `merge_cells`: Merge cell ranges
- `unmerge_cells`: Unmerge cell ranges
- `get_merged_cell_ranges`: List merged ranges

### Format Tools
- `format_range`: Apply cell formatting
- `apply_data_validation`: Set data validation rules
- `get_validation_info`: Get validation information

### Advanced Tools
- `create_chart`: Create charts from data
- `create_pivot_table_tool`: Create pivot tables
- `create_table`: Create Excel tables

### MinIO Tools
- `list_minio_files`: List cloud files for user
- `pull_minio_file`: Download files from cloud
- `push_minio_file`: Upload files to cloud

### Agent Management Tools
- `list_available_tools_for_agent`: Get tools for specific agent type
- `get_agent_profiles`: List available agent profiles

## 🔧 Development

### Running Tests

```bash
# Install dependencies
pip install -r requirements.txt

# Test server startup
python3 server.py --help

# Verify all tools are registered (should show 25 tools)
python3 -c "from src.server import ExcelMCPServer; s=ExcelMCPServer(); print(f'Registered {len(s.mcp._tool_tags)} tools')"
```

### Adding New Tools

1. Create tool function with proper tagging:

```python
@mcp_server.tool(
    tags=ToolTags(
        functional_domains=["excel"],
        permissions=["write"],
        resource_types=["data"],
        scopes=["user_scoped"]
    )
)
def my_new_tool(user_id: str, filename: str, ...) -> str:
    """Tool description."""
    safe_filename = get_safe_filename(filename)
    file_path = mcp_server.file_manager.get_file_path(safe_filename, user_id)
    
    with mcp_server.file_manager.lock_file(file_path):
        # Tool implementation
        pass
    
    return f"Operation completed on '{safe_filename}'"
```

2. Register in appropriate tool module
3. Update agent profiles if needed

### Custom Agent Profiles

```python
from src.core.tag_system import create_custom_agent

# Create custom agent
custom_agent = create_custom_agent(
    "My Custom Agent",
    ["excel", "read", "chart", "user_scoped"]
)

# Use with server
server.set_agent_context(custom_tags=["excel", "read", "chart", "user_scoped"])
```

## 🔄 Migration from v1.x

### Breaking Changes

1. **Project Structure**: Moved to `src/` architecture
2. **Tool Registration**: Tools now use tag-based registration
3. **File Paths**: Functions return filenames instead of full paths
4. **Agent Filtering**: Tools are filtered based on agent type
5. **File Locking**: All file operations now use locking
6. **Import Paths**: Update imports to use `src.` prefix

### Migration Steps

1. Update your MCP client to handle the new tool filtering
2. Specify agent type when connecting to server
3. Update any code expecting full file paths to use filenames
4. Test with the new concurrent access patterns

## 📋 Requirements

- Python 3.9+
- FastMCP 2.0+
- openpyxl 3.1.5+
- minio 7.1.0+
- PyYAML 6.0+

## 🤝 Contributing

1. Follow the existing code structure
2. Add appropriate tags to new tools
3. Include proper file locking for file operations
4. Return safe filenames, not full paths
5. Add tests for new functionality

## 📄 License

Same as original project license.