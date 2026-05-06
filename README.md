
# CKAN MCP Server

> Work inspired by ondics [ckan-mcp-server](https://github.com/ondics/ckan-mcp-server) but largely refactored to include more features and improvements.

A Model Context Protocol (MCP) server for the CKAN API that enables browsing and managing CKAN data portals through MCP-compatible clients.

## What is this?

This is an MCP server that provides access to CKAN (Comprehensive Knowledge Archive Network) APIs through the Model Context Protocol. It can be used with MCP-compatible clients like Claude Desktop, IDEs, or other AI applications to interact with CKAN data portals.

## Features

✅ **Complete CKAN API Coverage**
- Package/dataset search and management
- Resource retrieval and downloading
- Organization and user management
- Tag and vocabulary management
- Full CRUD operations

✅ **Resource Download with Streaming**
- Download resources to disk with `ckan_resource_download`
- Automatic filename generation from resource metadata
- Streaming downloads for large files
- Support for multiple file formats

✅ **Secure & Flexible**
- API key authentication
- Basic auth support
- SSL certificate verification
- Environment-based configuration

✅ **Production Ready**
- Async/await architecture
- Proper error handling
- Comprehensive logging
- Docker support

## Quick Start

### Installation

```bash
# Using uv (recommended)
uv pip install ckan-mcp-server

# Or using pip
pip install ckan-mcp-server
```

### Configuration

```bash
# Copy and edit environment
cp .env.sample .env

# Edit with your CKAN details
export CKAN_URL=https://demo.ckan.org
export CKAN_API_KEY=your-api-key
```

### Running the Server

```bash
# Direct
python -m src.mcp_ckan_server

# Using uv
uv run python -m src.mcp_ckan_server

# Docker
docker compose up
```

### Using with Claude Desktop

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "ckan": {
      "command": "python",
      "args": ["-m", "src.mcp_ckan_server"],
      "env": {
        "CKAN_URL": "https://demo.ckan.org",
        "CKAN_API_KEY": "your-key"
      }
    }
  }
}
```

## Project Structure

```
ckan-mcp-server/
├── src/                          # Main implementation
│   ├── mcp_ckan_server.py       # MCP server & tools
│   └── __init__.py
├── tests/                        # Test suite
│   ├── test_resource_download.py
│   └── test_download_pacificdata.py
├── examples/                     # Usage examples
│   ├── example_resource_dump.py
│   └── test_download_pacificdata.py
├── docs/                         # Documentation
│   ├── RESOURCE_DOWNLOAD.md
│   └── README.md
├── CONTRIBUTING.md              # Contribution guide
├── README.md                     # This file
└── pyproject.toml               # Project config
```

See detailed guides:
- [📚 Documentation](./docs/README.md)
- [🔧 Source Code](./src/README.md)
- [📋 Tests](./tests/README.md)
- [💡 Examples](./examples/README.md)
- [🤝 Contributing](./CONTRIBUTING.md)
```

### Using Docker Compose
```bash
# Copy environment file and configure
cp .env.example .env
# Edit .env with your settings

# Run the server
docker-compose up
```

## Available Tools

The MCP server provides the following tools:

### Packages/Datasets
- `ckan_package_list`: List all packages
- `ckan_package_show`: Show details of a specific package
- `ckan_package_search`: Search for packages

### Organizations
- `ckan_organization_list`: List all organizations
- `ckan_organization_show`: Show organization details

### DataStore
- `ckan_datastore_search` Search DataStore Tables by Resource

### Groups and Tags
- `ckan_group_list`: List all groups
- `ckan_tag_list`: List all tags

### Resources
- `ckan_resource_show`: Show resource details

### System
- `ckan_site_read`: Site information
- `ckan_status_show`: Status and version information

## Examples

### Search packages
```json
{
  "tool": "ckan_package_search",
  "arguments": {
    "q": "climate data",
    "rows": 5,
    "sort": "score desc"
  }
}
```

### Show organization
```json
{
  "tool": "ckan_organization_show",
  "arguments": {
    "id": "sample-organization",
    "include_datasets": true
  }
}
```

### List all tags
```json
{
  "tool": "ckan_tag_list",
  "arguments": {}
}
```

## Resources

The server also provides the following resources:
- `ckan://api/docs`: API documentation
- `ckan://config`: Server configuration

## Using with MCP Clients

### Claude Desktop

Add this to your Claude Desktop configuration file:

```json
{
  "mcpServers": {
    "ckan": {
      "command": "python",
      "args": ["/path/to/mcp_ckan_server.py"],
      "env": {
        "CKAN_URL": "https://demo.ckan.org",
        "CKAN_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

### Other MCP Clients

The server communicates via stdio, so any MCP-compatible client can connect to it by running the Python script and communicating through standard input/output.

## CKAN API Reference

This MCP server implements the main endpoints of the CKAN API v3. 
Complete documentation: https://docs.ckan.org/en/latest/api/

## License

Mozilla Public License Version 2.0

## Author

(C) 2025, Ondics GmbH, https://ondics.de
