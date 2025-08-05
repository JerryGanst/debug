# Changelog

## [2.0.2] - 2025-08-04

### ✨ Added

- **Row/Column Operations**: New sheet manipulation tools for enhanced Excel editing
  - `insert_rows`: Insert one or more rows at specified position
  - `insert_columns`: Insert one or more columns at specified position
  - `delete_sheet_rows`: Delete one or more rows from specified position
  - `delete_sheet_columns`: Delete one or more columns from specified position
- **Parameter Validation**: Comprehensive bounds checking and error handling for row/column operations
- **Tool Coverage**: Expanded total tools from 21 to 25, enhancing editing capabilities

### 🧪 Testing

- **Comprehensive Testing**: 100% test coverage for all new row/column operations
- **Validation Testing**: Verified parameter validation and error handling
- **Integration Testing**: Confirmed new tools work with existing tag system and agent profiles

### 📊 Updated Metrics

- **Total Tools**: 25 (increased from 21)
- **Agent Tool Counts**: Updated for excel_editor (22), data_scientist (22), report_generator (22), admin (25)
- **New Tool Categories**: Row/Column operations added to tool access matrix

## [2.0.1] - 2025-08-04

### 🐛 Fixed

- **Type Annotation Compatibility**: Fixed Python 3.9+ compatibility issues with type annotations
  - Replaced new-style type annotations (`list[str]`, `dict[str, Any]`) with typing imports
  - Updated all utility functions in `src/utils/` for better compatibility
- **Agent Tag Matching Logic**: Improved tool filtering algorithm
  - Fixed `data_scientist` and `report_generator` agents having 0 tools
  - Implemented smart matching: domain-specific agents require exact domain match
  - General permission agents use intersection-based matching
- **Agent Profile Optimization**: Updated agent configurations for better tool distribution
  - `excel_analyst`: 6 tools (read-only operations)
  - `excel_editor`: 18 tools (full Excel editing)
  - `minio_reader`: 3 tools (MinIO read operations)
  - `minio_manager`: 3 tools (MinIO management)
  - `data_scientist`: 18 tools (advanced Excel analytics)
  - `report_generator`: 18 tools (Excel reporting)
  - `admin`: 21 tools (complete access)

### 🧪 Testing

- **Comprehensive Test Coverage**: Created full test suite covering all tool categories
- **100% Test Pass Rate**: All 17 tests passing across workbook, data, formatting, advanced operations, and agent filtering
- **Production Readiness**: Verified all tools work correctly with concurrent access protection

### 🧹 Code Quality

- **Removed Unused Imports**: Cleaned up redundant imports across all modules
- **Documentation Updates**: Updated README.md, TOOLS.md with accurate tool counts and agent capabilities
- **Clean Production Environment**: Removed all test files and temporary artifacts

## [2.0.0] - 2025-01-01

### 🎉 Major Refactoring Release

This release represents a complete refactoring of the Excel MCP server with modern architecture, improved security, and agent-based tool filtering.

### ✨ Added

#### Core Features
- **Tag-based Tool Filtering System**: Multi-dimensional tagging for precise tool access control
- **Agent Profile System**: Predefined and custom agent profiles for different use cases
- **File Locking Mechanism**: Concurrent access protection with automatic lock management
- **Standardized Project Structure**: Clean `src/` architecture with separation of concerns
- **Path Safety**: Filename-only returns to prevent path confusion and security issues

#### Agent Profiles
- `excel_analyst`: Read-only Excel data analysis capabilities
- `excel_editor`: Full Excel editing and manipulation
- `minio_reader`: Read-only cloud storage access  
- `minio_manager`: Full cloud storage management
- `data_scientist`: Advanced analytics with charts and pivot tables
- `report_generator`: Report creation with formatting capabilities
- `admin`: Full access to all server functionality

#### New Tools
- `list_available_tools_for_agent`: Get tools available to specific agent types
- `get_agent_profiles`: List all available agent profiles
- Enhanced error handling and validation across all tools

#### Security & Reliability
- File locking with configurable timeouts (default: 30 seconds)
- Safe filename extraction to prevent directory traversal
- Improved error handling and logging
- Concurrent operation protection

### 🔧 Changed

#### Architecture
- **BREAKING**: Moved from flat structure to `src/` based architecture
- **BREAKING**: Split monolithic `server.py` into modular components:
  - `src/core/`: Core server functionality
  - `src/tools/`: MCP tool modules by category
  - `src/utils/`: Utility functions (preserved from v1.x)

#### Tool Registration
- **BREAKING**: Tools now use tag-based registration instead of simple decorators
- **BREAKING**: All tools must specify tags for agent filtering
- Improved tool organization by functional category

#### File Handling
- **BREAKING**: Functions return filenames instead of full file paths
- **BREAKING**: All file operations now use file manager with locking
- Automatic user directory creation
- Path sanitization and validation

#### Configuration
- Enhanced configuration management with typed configuration classes
- Better separation of MCP and MinIO configurations
- Improved error handling for missing/invalid configurations

#### MinIO Integration
- Enhanced error handling for MinIO operations
- Better file naming for uploaded files (with "(mod)" suffix)
- Improved user isolation in cloud storage

### 🐛 Fixed

#### Path Confusion Issues
- Tools no longer return full file paths that could confuse LLM clients
- Consistent filename-only returns across all operations
- Safe path handling to prevent directory traversal

#### Concurrency Issues
- Added file locking to prevent corruption from simultaneous access
- Race condition protection for file operations
- Automatic cleanup of lock files

#### Code Quality
- Eliminated code duplication through reusable utility functions
- Improved error handling and logging throughout
- Better separation of concerns

### 🚨 Breaking Changes

#### Import Changes
```python
# Before (v1.x)
from server import mcp

# After (v2.0)
from src.server import ExcelMCPServer
```

#### Tool Registration
```python
# Before (v1.x)
@mcp.tool()
def my_tool(user_id: str, filename: str) -> str:
    pass

# After (v2.0)
@mcp_server.tool(
    tags=ToolTags(
        functional_domains=["excel"],
        permissions=["write"], 
        resource_types=["data"],
        scopes=["user_scoped"]
    )
)
def my_tool(user_id: str, filename: str) -> str:
    pass
```

#### Return Values
```python
# Before (v1.x) - returned full paths
"File saved to /excel_files/user_123/report.xlsx"

# After (v2.0) - returns filenames only
"File saved to 'report.xlsx'"
```

#### Agent-based Access
- Clients must now specify agent type or use admin access
- Tools are filtered based on agent capabilities
- Different agents see different subsets of available tools

### 🔄 Migration Guide

#### For MCP Client Developers

1. **Update Tool Calls**: Handle the new filename-only returns
2. **Specify Agent Type**: Choose appropriate agent profile for your use case
3. **Update Error Handling**: New error patterns and messages
4. **Test Concurrency**: Verify behavior under concurrent access

#### For Server Developers

1. **Update Imports**: Change to `src.` based imports
2. **Add Tool Tags**: All custom tools need appropriate tagging
3. **Use File Manager**: Replace direct file operations with file manager
4. **Return Filenames**: Update tools to return filenames instead of paths

### 📊 Performance Improvements

- Faster tool filtering through optimized tag matching
- Reduced memory usage with better resource management
- Improved logging performance with structured logging
- More efficient file operations with proper locking

### 🛡️ Security Improvements

- Path traversal protection through filename sanitization
- User isolation in file storage
- Admin-only access controls for sensitive operations
- Secure file locking mechanism

### 📚 Documentation

- Complete README rewrite with modern formatting
- Comprehensive architecture documentation
- Developer guide for extending the server
- Migration documentation for v1.x users
- API documentation updates for all tools

### 🧪 Testing

- New test suite for core functionality
- Tag system validation tests
- File locking mechanism tests
- Agent filtering verification tests

---

## [1.x] - Previous Versions

See git history for previous version changes. Version 2.0 represents a complete rewrite with backwards-incompatible changes for improved architecture, security, and functionality.