# Copilot Instructions for CKAN MCP Server

## Quick Reference

**Project**: CKAN MCP Server - A Model Context Protocol (MCP) server for the CKAN API  
**Language**: Python 3.13+  
**Main File**: `src/mcp_ckan_server.py` (~780 lines)  
**Package Manager**: `uv`

## Build & Deployment

### Local Development
```bash
# Install and sync dependencies
uv sync

# Run the server directly
uv run ckan-mcp-server --transport stdio

# Configuration: Set environment variables or copy .env.example to .env
# Required: CKAN_URL, CKAN_API_KEY (optional)
```

### Docker
```bash
# Local development (build from source)
docker compose --profile stdio up --build

# Production deployment from internal registry
CKAN_MCP_IMAGE=docker-repo.spc.int/pdh-repo/ckan-mcp-server \
  docker compose -f docker-compose.yml -f docker-compose.prod.yml --profile stdio up --no-build
```

**Note**: `docker-compose.yml` is the local-dev default (`build: .`). `docker-compose.prod.yml` overlays registry images for deployment. Use `--profile <name>` to select stdio or SSE.

### Publishing
```bash
# Build and publish to PyPI (requires PYPI_API_TOKEN in .env)
make publish-pypi
```

## Testing

The project includes an agent-based test in `tests/test.py` that demonstrates the MCP server integration with an AI agent framework. Run it with:
```bash
python -m pytest tests/test.py        # If pytest is available
python tests/test.py                   # Or run directly (uses agent framework)
```

Note: Tests require the `agents` package and working CKAN connection.

## Architecture & Design Patterns

### Core Components

1. **CKANAPIClient** (lines 28-76)
   - Async HTTP client for CKAN API v3
   - Context manager pattern: `async with CKANAPIClient(...) as client:`
   - Handles SSL context via certifi, basic auth, and API key auth
   - All requests to `/api/3/action/` endpoints
   - Returns parsed JSON; raises exceptions on API errors

2. **MCP Server Setup** (lines 82+)
   - Uses `mcp.server.Server` class
   - Three main handlers:
     - `@app.list_tools()` - Registers available CKAN operations
     - `@app.call_tool(name, arguments)` - Dispatches tool calls with argument validation
     - `@app.list_resources()` - Provides static resources (API docs, config)
     - `@app.read_resource(uri)` - Serves resource content

3. **Tool Registration Pattern**
   - Each tool maps to a CKAN API endpoint
   - Schema validation via `inputSchema` (JSON Schema)
   - Supports both GET and POST operations
   - Error handling returns TextContent with error message

### Async Architecture
- All major operations are async (HTTP, server I/O)
- Uses `aiohttp.ClientSession` for connection pooling
- MCP server runs via `mcp.server.stdio` or custom transport (HTTP/SSE)

## Key Conventions

### Tool Naming
- Prefix: `ckan_` 
- Pattern: `ckan_<resource>_<action>` (e.g., `ckan_package_search`, `ckan_organization_list`)
- Naming must match endpoint checks in `handle_call_tool()` (lines 401-465)

### Adding New Tools
1. Define tool in `handle_list_tools()` with name, description, inputSchema
2. Add corresponding `elif name == "ckan_<tool>"` block in `handle_call_tool()`
3. Construct endpoint URL and call `ckan_client._make_request()`
4. Return `types.TextContent(type="text", text=json.dumps(result))`

Example:
```python
types.Tool(
    name="ckan_custom_action",
    description="Description of what it does",
    inputSchema={
        "type": "object",
        "properties": {
            "param1": {"type": "string", "description": "..."}
        },
        "required": ["param1"]
    }
)
```

### Configuration
- Environment-driven: `CKAN_URL`, `CKAN_API_KEY`, `CKAN_BASIC_AUTH_USERNAME`, `CKAN_BASIC_AUTH_PASSWORD`
- Load via `python-dotenv`: `load_dotenv()` reads `.env` file
- SSL certificates pinned to system certifi store

### API Request Flow
```
Tool input → CKANAPIClient._make_request(method, endpoint, data)
  → aiohttp.ClientSession.request()
  → Response JSON parsed
  → result.get('result') extracted
  → TextContent returned to MCP client
```

### Error Handling
- HTTP/connection errors: `aiohttp.ClientError` → wrapped with context
- API errors: Check `result.get('success', False)`; extract `error` dict
- All exceptions logged via logger and returned as TextContent errors

## Dependencies

**Core (pyproject.toml)**:
- `mcp>=1.19.0` - Model Context Protocol framework
- `aiohttp>=3.13.1` - Async HTTP client
- `python-dotenv>=1.1.0` - Environment configuration
- `certifi>=2026.2.25` - SSL certificate bundle
- `uv>=0.8.9` - Package manager

**Build**:
- `setuptools>=61.0` - Used for build backend
- `ckanapi` - CKAN API client (listed in build-system)

## File Descriptions

| File | Purpose |
|------|---------|
| `src/mcp_ckan_server.py` | Main server implementation, all logic in one file |
| `pyproject.toml` | Project metadata, dependencies, build config |
| `requirements.txt` | Simplified pip-compatible dependency list |
| `Dockerfile` | Container image for running the server |
| `docker-compose.yml` | Local development compose file (build from source) |
| `docker-compose.prod.yml` | Production compose overlay (pull from registry image) |
| `Makefile` | Build targets for Docker and PyPI publishing |
| `tests/test.py` | Agent-based integration test |

## Common Tasks

### Add a new CKAN API endpoint
1. Add `types.Tool()` definition in `handle_list_tools()` 
2. Add matching `elif name == "..."` in `handle_call_tool()` with endpoint construction
3. Test via MCP client (e.g., Claude Desktop)

### Debug API calls
- Enable debug logging: Set `logpath` and `loglevel` when starting server
- Check stderr for `logger.debug()` and `logger.error()` output
- API responses logged before `success` check

### Test against different CKAN instances
- Update `.env`: `CKAN_URL=https://different-instance.org`
- Restart server, tools will use new endpoint
- API key optional for read-only operations

### Deploy as MCP Server in Claude Desktop
Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "ckan": {
      "command": "ckan-mcp-server",
      "args": ["--transport", "stdio"],
      "env": {
        "CKAN_URL": "https://your-ckan-instance.org",
        "CKAN_API_KEY": "your-key"
      }
    }
  }
}
```

## Development Notes

- Single-file design: All code in `src/mcp_ckan_server.py` for simplicity and deployment
- Package entrypoint is `ckan-mcp-server` via `src/mcp_ckan_server.py`
- No client-side caching in the server; caching happens at MCP client level
- CKAN API v3 only; endpoints use `/api/3/action/` format
- Query string construction: Manual `&`.join() for GET params (lines 412-417)
- POST data: Passed as JSON in request body (datastore operations)

## Known Limitations & TODOs

- Datastore create/update/upsert/delete operations marked as untested (lines 455-462)
- Query string building is manual; could use `urlencode()` for robustness
- No request rate limiting or retry logic
- Large result sets not paginated server-side (pagination handled by client)
