# Excel MCP Server

A powerful Model Context Protocol (MCP) server that provides comprehensive Excel file manipulation capabilities through MinIO cloud storage integration.

## Features

- **Excel File Operations**: Create, read, write, and manipulate Excel workbooks and worksheets
- **Advanced Formatting**: Cell styling, borders, fonts, colors, and conditional formatting
- **Data Analysis**: Pivot tables, charts, and Excel tables
- **Formula Management**: Apply and validate Excel formulas
- **Cloud Storage**: Seamless integration with MinIO for file persistence
- **User Isolation**: Secure file management with user-specific storage
- **Comprehensive API**: 30+ tools covering all major Excel operations

## Architecture

The server follows a clean architecture pattern with:
- **Tools Layer**: Excel manipulation tools organized by functionality
- **Core Layer**: File management and MCP server configuration
- **Utils Layer**: Excel operation implementations
- **MinIO Integration**: Cloud storage for file persistence

## Installation

### Prerequisites

- Python 3.10+
- MinIO server or compatible S3 storage
- Virtual environment (recommended)

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Luxshare-ai-mcp-github
   ```

2. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Configure MinIO settings**
   Create a `configs.yaml` file based on `configs_sample.yaml`:
   ```yaml
   minio:
     endpoint: "localhost:9000"
     access_key: "your-access-key"
     secret_key: "your-secret-key"
     bucket: "excel-files"
     secure: false
   ```

## Usage

### Starting the Server

```bash
python server.py
```

The server will start and register all Excel manipulation tools with the MCP protocol.

### Available Tools

The server provides tools in the following categories:

- **MinIO Storage Operations**: File upload/download from cloud storage
- **Workbook Operations**: Create and manage Excel workbooks
- **Data Operations**: Read/write data to worksheets
- **Formatting Operations**: Cell styling and formatting
- **Formula Operations**: Excel formula management
- **Chart Operations**: Create charts and graphs
- **Pivot Table Operations**: Data analysis and summarization
- **Table Operations**: Create structured Excel tables
- **Worksheet Operations**: Manage individual worksheets
- **Range Operations**: Work with cell ranges
- **Row and Column Operations**: Insert/delete rows and columns

For detailed tool documentation, see [TOOLS.md](TOOLS.md).

## File Management

### Local vs Cloud Storage

- **Local Storage**: Temporary files for active operations
- **MinIO Storage**: Permanent file storage with user isolation
- **File Cleanup**: Automatic cleanup of local temporary files

### User File Organization

Files are organized in MinIO using the pattern:
```
bucket/
└── private/
    └── {user_id}/
        ├── file1.xlsx
        ├── file2.xlsx
        └── ...
```

## Cleanup Mechanism

### Temporary File Cleanup

When the server is shut down using `Ctrl+C`, it automatically cleans up all temporary local files because:

1. **All user files are stored in MinIO**: The primary storage is cloud-based
2. **Local files are temporary**: Only used during active operations
3. **Automatic cleanup**: Prevents disk space accumulation
4. **Data safety**: No data loss as files are persisted in MinIO

### Cleanup Process

1. **Signal Handling**: Server catches `SIGINT` (Ctrl+C) signal
2. **File Cleanup**: Removes all temporary Excel files from local storage
3. **Graceful Shutdown**: Closes connections and exits cleanly

### Benefits

- **Disk Space Management**: Prevents accumulation of temporary files
- **Clean Environment**: Fresh start on each server restart
- **Data Persistence**: User files remain safe in MinIO storage
- **Resource Efficiency**: Optimizes local storage usage

## Configuration

### Environment Variables

- `MINIO_ENDPOINT`: MinIO server endpoint
- `MINIO_ACCESS_KEY`: MinIO access key
- `MINIO_SECRET_KEY`: MinIO secret key
- `MINIO_BUCKET`: MinIO bucket name
- `MINIO_SECURE`: Use HTTPS (true/false)

### Configuration File

The server can be configured using a YAML configuration file:

```yaml
minio:
  endpoint: "localhost:9000"
  access_key: "your-access-key"
  secret_key: "your-secret-key"
  bucket: "excel-files"
  secure: false

server:
  host: "localhost"
  port: 8000
  debug: false
```

## Development

### Project Structure

```
src/
├── core/           # Core server and file management
├── tools/          # MCP tool implementations
└── utils/          # Excel operation utilities
```

### Adding New Tools

1. Implement the tool function in the appropriate module
2. Register it in the corresponding tool registration function
3. Update the TOOLS.md documentation
4. Add appropriate error handling and validation

### Testing

```bash
# Run tests (if available)
python -m pytest

# Run with coverage
python -m pytest --cov=src
```

## Security Features

- **User Isolation**: Files are segregated by user ID
- **Path Sanitization**: Prevents directory traversal attacks
- **File Locking**: Prevents concurrent access conflicts
- **Safe file_names**: Automatic file_name sanitization

## Error Handling

The server provides comprehensive error handling:
- **Validation Errors**: Input parameter validation
- **File Errors**: File operation error handling
- **MinIO Errors**: Storage operation error handling
- **User-Friendly Messages**: Clear error messages without path exposure

## Performance Considerations

- **File Locking**: Prevents concurrent access issues
- **Efficient Operations**: Optimized Excel operations
- **Memory Management**: Proper resource cleanup
- **Async Operations**: Non-blocking file operations

## Troubleshooting

### Common Issues

1. **MinIO Connection Failed**
   - Check MinIO server status
   - Verify endpoint and credentials
   - Ensure bucket exists

2. **File Permission Errors**
   - Check local directory permissions
   - Verify MinIO bucket permissions
   - Ensure user has write access

3. **Memory Issues**
   - Large Excel files may require more memory
   - Consider file size limits
   - Monitor server resource usage

### Logs

The server provides detailed logging for debugging:
- Tool execution logs
- Error and exception logs
- File operation logs
- MinIO operation logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request