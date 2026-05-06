# Resource Download / Dump Feature

This document describes how to use the CKAN MCP Server to download and dump resources from CKAN instances using the `ckanapi` library.

## Overview

The CKAN MCP Server provides several tools to work with resources:

1. **`ckan_resource_show`** - Get metadata for a single resource (URL, format, size, etc.)
2. **`ckan_resource_download`** - Download and optionally parse a resource
3. **Direct RemoteCKAN access** - Use the underlying `ckanapi.RemoteCKAN` client for advanced operations

## Tools

### ckan_resource_show

Get detailed information about a single resource, including its download URL.

**Input:**
```json
{
  "id": "resource-id-or-uuid"
}
```

**Output:**
```json
{
  "id": "resource-id",
  "name": "Resource Name",
  "url": "https://example.com/data.csv",
  "format": "CSV",
  "description": "Resource description",
  "size": 12345,
  "last_modified": "2024-01-15T10:30:00",
  "package_id": "dataset-id",
  ...
}
```

### ckan_resource_download

Download a single resource with optional parsing.

**Input:**
```json
{
  "resource_id": "resource-id-or-uuid",
  "output_format": "raw"  // or "json"
}
```

**Parameters:**
- `resource_id` (required): UUID or ID of the resource to download
- `output_format` (optional, default: "raw"): 
  - `"raw"` - Returns resource metadata and direct download URL
  - `"json"` - Downloads and parses the resource as JSON

**Output with `output_format: "raw"`:**
```json
{
  "id": "resource-id",
  "name": "Resource Name",
  "url": "https://example.com/data.csv",
  "format": "CSV",
  ...
}
```

**Output with `output_format: "json"`:**
```json
{
  "resource_metadata": {
    "id": "resource-id",
    "name": "Resource Name",
    "url": "https://example.com/data.json",
    ...
  },
  "data": [
    {"field1": "value1", "field2": "value2"},
    {"field1": "value3", "field2": "value4"}
  ]
}
```

## Usage Examples

### Example 1: Get Resource Information

Find the download URL for a resource:

```python
import asyncio
from mcp_ckan_server import CKANAPIClient

async def get_resource_info():
    client = CKANAPIClient('https://your-ckan.org')
    async with client:
        # Get resource metadata
        resource = await client.call_action(
            "resource_show",
            id="your-resource-id"
        )
        print(f"Resource: {resource['name']}")
        print(f"Download URL: {resource['url']}")
        print(f"Format: {resource['format']}")

asyncio.run(get_resource_info())
```

### Example 2: Download and Parse JSON Resource

Download a JSON resource and parse it:

```python
async def download_json_resource():
    client = CKANAPIClient('https://your-ckan.org')
    async with client:
        # Download and parse JSON
        result = await client.call_action(
            "resource_download",
            resource_id="your-resource-id",
            output_format="json"
        )
        data = result['data']
        metadata = result['resource_metadata']
        
        print(f"Downloaded: {metadata['name']}")
        print(f"Records: {len(data)}")
        for record in data[:5]:
            print(record)

asyncio.run(download_json_resource())
```

### Example 3: Using RemoteCKAN Directly

For advanced resource operations, use the underlying `ckanapi.RemoteCKAN` client:

```python
async def advanced_download():
    client = CKANAPIClient('https://your-ckan.org')
    async with client:
        # Get resource info
        resource = await client.call_action("resource_show", id="resource-id")
        
        # Download using the session
        url = resource['url']
        response = client.client.session.get(url)
        
        # Save to file
        with open(f"downloaded_{resource['id']}.bin", 'wb') as f:
            f.write(response.content)

asyncio.run(advanced_download())
```

### Example 4: Find and Download Resources by Format

Search for CSV resources and download them:

```python
async def download_csv_resources():
    client = CKANAPIClient('https://your-ckan.org')
    async with client:
        # Search for packages with CSV resources
        search = await client.call_action(
            "package_search",
            q='+res_format:CSV',
            rows=10
        )
        
        for package in search['results']:
            for resource in package.get('resources', []):
                if resource.get('format', '').upper() == 'CSV':
                    meta = await client.call_action(
                        "resource_show",
                        id=resource['id']
                    )
                    print(f"Found: {meta['name']} ({meta['url']})")
                    
                    # Download it
                    response = client.client.session.get(meta['url'])
                    filename = f"{meta['name']}.csv"
                    with open(filename, 'wb') as f:
                        f.write(response.content)
                    print(f"Saved: {filename}")

asyncio.run(download_csv_resources())
```

## MCP Client Integration

When using the MCP Server with clients like Claude Desktop or other MCP tools, you can call the tools directly:

```json
{
  "name": "ckan_resource_show",
  "arguments": {
    "id": "abc123def456"
  }
}
```

Or for download with parsing:

```json
{
  "name": "ckan_resource_download",
  "arguments": {
    "resource_id": "abc123def456",
    "output_format": "json"
  }
}
```

## Authentication

Resources can be protected by CKAN permissions. For private resources, use API key authentication:

```python
client = CKANAPIClient(
    'https://your-ckan.org',
    api_key='your-api-key'
)
```

Or basic HTTP authentication:

```python
client = CKANAPIClient(
    'https://your-ckan.org',
    basic_auth_username='user',
    basic_auth_password='password'
)
```

## Best Practices

1. **Check resource format** before attempting to parse as JSON
2. **Handle large files** - Use streaming or download in chunks for large resources
3. **Verify URLs** - Some resources may have broken or external URLs
4. **Rate limiting** - Be respectful of CKAN server resources
5. **Cache results** - Store downloaded data locally to reduce repeated API calls

## Error Handling

Common errors when downloading resources:

- **Resource not found** - Invalid resource ID
- **URL broken** - Resource URL is invalid or external link is down
- **Invalid JSON** - Resource claims to be JSON but isn't
- **Authentication required** - Resource requires API key
- **Server error** - CKAN instance is down or has issues

## Related ckanapi Features

The underlying `ckanapi` library provides additional functionality:

- **`ckanapi.cli.dump`** - CLI tool to dump datasets/resources to files
- **`RemoteCKAN.session`** - Direct HTTP session for custom requests
- **`ckanapi.LocalCKAN`** - Direct database access for local CKAN instances
- **Parallel downloads** - Use worker pools for bulk operations

See [ckanapi documentation](https://github.com/ckan/ckanapi) for more details.
