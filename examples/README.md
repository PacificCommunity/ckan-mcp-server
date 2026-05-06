# Examples

Practical examples demonstrating how to use the CKAN MCP Server.

## Files

- **example_resource_dump.py** - Examples of downloading and processing resources
  - Using `CKANAPIClient` directly
  - Resource metadata retrieval
  - File downloads with different formats

- **test_download_pacificdata.py** - Integration test with real CKAN instance
  - Demonstrates MCP tool usage
  - Downloads resources to disk
  - Shows error handling

## Running Examples

### Download resources from a CKAN instance

```bash
cd examples
python example_resource_dump.py
```

Requires environment variables:
```bash
export CKAN_URL=https://demo.ckan.org
export CKAN_API_KEY=your-key
```

### Test resource download

```bash
cd examples
python test_download_pacificdata.py
```

Configuration from `.env` file:
```
CKAN_URL=https://pacificdata.org/data
CKAN_API_KEY=your-key
```

## Common Patterns

### Search and Download

```python
from ckan_mcp_server import CKANAPIClient

async def search_and_download():
    client = CKANAPIClient("https://demo.ckan.org", api_key="key")
    
    async with client as c:
        # Search for datasets
        results = await client.call_action(
            "package_search",
            q="GeoJSON"
        )
        
        # Get first dataset's first resource
        if results['results']:
            pkg = results['results'][0]
            if pkg.get('resources'):
                resource_id = pkg['resources'][0]['id']
                
                # Get resource metadata
                resource = await client.call_action(
                    "resource_show",
                    id=resource_id
                )
                print(f"Resource: {resource['name']}")
                print(f"Format: {resource['format']}")
```

### File Download via MCP Tool

```python
import mcp_ckan_server
import json

# Initialize client
mcp_ckan_server.ckan_client = CKANAPIClient(url, api_key)

# Call MCP tool
result = await mcp_ckan_server.handle_call_tool(
    "ckan_resource_download",
    {
        "resource_id": "17b39833-1d29-4d89-ac1a-55c536ada7a4",
        "output_folder": "/tmp/downloads",
        "output_format": "file"
    }
)

# Parse result
if isinstance(result, list):
    result_data = json.loads(result[0].text)
    print(f"Downloaded to: {result_data['file_path']}")
```

## More Examples

See the main README for additional patterns and use cases.
