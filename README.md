# Excel MCP Server

An MCP (Model Context Protocol) server for manipulating Excel files with multi-user support and MinIO integration.

## Features

- Full Excel file manipulation (read, write, format, formulas, charts, pivot tables)
- Multi-user support with isolated file storage
- MinIO integration for cloud storage
- HTTP transport only (simplified from previous versions)

## Configuration

All configuration is loaded from `configs.yaml`:

```yaml
MCP_CONFIG:
  EXCEL_FILES_PATH: ./excel_files
  PORT: 3210
  HOST: 0.0.0.0
  LOG_LEVEL: debug

MINIO_CONFIG:
  MINIO_ENDPOINT: http://10.180.248.141:9000
  MINIO_ACCESS_KEY: minioadmin
  MINIO_SECRET_KEY: G3j+-G]aMX%bc/Wt
  MINIO_BUCKET: ai-file
```

## File Organization

Files are organized by user ID:
- Pattern: `/excel_files/user_<user_id>/<filename>`
- Example: `/excel_files/12345678/transcript.xlsx`

## Starting the Server

```bash
python3 server.py
```

## Usage

All tools require a `user_id` as the first parameter. See `TOOLS.md` for detailed documentation of all available tools.

use client.py to check if the server is running properly:

python3 client.py