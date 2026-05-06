# Documentation

Complete documentation for the CKAN MCP Server project.

## Guides

- **[RESOURCE_DOWNLOAD.md](./RESOURCE_DOWNLOAD.md)** - Resource download feature documentation
  - Output formats (raw, json, file)
  - Authentication methods
  - Error handling
  - Best practices
  - Performance considerations

- **[CHANGELOG_RESOURCE_DUMP.md](./CHANGELOG_RESOURCE_DUMP.md)** - Feature history
  - Resource dump implementation details
  - Version changes
  - Migration guide

## MCP Tool Reference

### Package Management

- `ckan_package_search` - Search for datasets
- `ckan_package_show` - Get dataset details
- `ckan_package_create` - Create new dataset
- `ckan_package_patch` - Update dataset metadata
- `ckan_package_delete` - Delete dataset

### Resource Management

- `ckan_resource_show` - Get resource metadata
- `ckan_resource_create` - Create new resource
- `ckan_resource_patch` - Update resource
- `ckan_resource_delete` - Delete resource
- **`ckan_resource_download`** - Download resource files to disk

### Organization Management

- `ckan_organization_list` - List organizations
- `ckan_organization_show` - Get organization details
- `ckan_organization_create` - Create organization
- `ckan_organization_patch` - Update organization
- `ckan_organization_delete` - Delete organization

### User & Permission Management

- `ckan_user_list` - List users
- `ckan_user_show` - Get user details
- `ckan_user_create` - Create user
- `ckan_group_list` - List groups
- `ckan_member_create` - Add member to group

### Metadata & Vocabularies

- `ckan_tag_list` - List all tags
- `ckan_tag_show` - Get tag details
- `ckan_tag_create` - Create tag
- `ckan_vocabulary_list` - List vocabularies
- `ckan_vocabulary_create` - Create vocabulary

## API Documentation

### CKANAPIClient

```python
class CKANAPIClient:
    """Async wrapper for CKAN API v3"""
    
    def __init__(
        self,
        url: str,
        api_key: Optional[str] = None,
        user_agent: Optional[str] = None,
        timeout: int = 30
    )
    
    async def call_action(
        self,
        action: str,
        **kwargs
    ) -> Dict[str, Any]
        """Call CKAN action, returns result data"""
    
    async def __aenter__() -> "CKANAPIClient"
        """Async context manager entry"""
    
    async def __aexit__()
        """Async context manager exit"""
```

### handle_call_tool

```python
async def handle_call_tool(
    name: str,
    arguments: Optional[Dict[str, Any]]
) -> List[types.TextContent]:
    """Dispatch MCP tool calls to CKAN API"""
```

## Configuration

### Environment Variables

```bash
# Required
CKAN_URL=https://your-ckan-instance.org

# Optional
CKAN_API_KEY=your-api-key
CKAN_BASIC_AUTH_USERNAME=username
CKAN_BASIC_AUTH_PASSWORD=password

# Logging
LOG_LEVEL=INFO
```

### .env File

```bash
cp .env.sample .env
# Edit .env with your settings
```

## Deployment

### Docker

```bash
# Run with docker-compose
docker compose --profile sse up

# Or manually
docker build -t ckan-mcp-server .
docker run -e CKAN_URL=https://your-instance.org ckan-mcp-server
```

### Systemd Service

Create `/etc/systemd/system/ckan-mcp.service`:

```ini
[Unit]
Description=CKAN MCP Server
After=network.target

[Service]
Type=simple
User=ckan
WorkingDirectory=/opt/ckan-mcp-server
ExecStart=/usr/local/bin/python -m src.mcp_ckan_server
EnvironmentFile=/opt/ckan-mcp-server/.env
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Start service:
```bash
sudo systemctl enable ckan-mcp
sudo systemctl start ckan-mcp
```

## Troubleshooting

### SSL Certificate Errors

The server uses `certifi` for SSL certificates. If you get certificate errors:

```bash
# Update certifi
pip install --upgrade certifi

# Or disable verification (not recommended for production)
export REQUESTS_CA_BUNDLE=
```

### Connection Refused

- Verify CKAN_URL is correct
- Check CKAN instance is running
- Verify network connectivity

### Authentication Errors

- Verify API key is valid
- Check key has required permissions
- Test key with curl:

```bash
curl -H "X-CKAN-API-Key: $CKAN_API_KEY" \
  https://your-instance.org/api/3/action/package_list
```

## Contributing

See CONTRIBUTING.md for development guidelines.

## License

See LICENSE file for details.
