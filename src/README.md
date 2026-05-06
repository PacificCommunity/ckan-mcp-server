# Source Code

This directory contains the main CKAN MCP Server implementation.

## Structure

- **mcp_ckan_server.py** - Main server implementation with all MCP tools and handlers
  - `CKANAPIClient` - Async HTTP client for CKAN API v3
  - `handle_call_tool()` - MCP tool dispatcher
  - MCP tool definitions and handlers

- **__init__.py** - Package initialization and exports

## Key Components

### CKANAPIClient

Async wrapper around `ckanapi.RemoteCKAN` for interacting with CKAN instances.

```python
from ckan_mcp_server import CKANAPIClient

client = CKANAPIClient(
    url="https://demo.ckan.org",
    api_key="your-api-key"
)

async with client as c:
    packages = await client.call_action("package_search", q="test")
```

### MCP Tools

Tools available through the MCP interface:

- `ckan_package_search` - Search for datasets
- `ckan_package_show` - Get dataset details
- `ckan_resource_show` - Get resource metadata
- `ckan_resource_download` - Download resource files to disk
- `ckan_organization_list` - List organizations
- And many more...

See main README for complete tool list.

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run server directly
python -m src.mcp_ckan_server

# Run tests
pytest tests/
```
