# Resource Download / Dump Feature - Changelog

## Summary

Added support for downloading and dumping individual resources from CKAN instances using the `ckanapi` library. This feature enables users to retrieve resource metadata and download resource files via the MCP server.

## What's New

### New MCP Tool: `ckan_resource_download`

Download a single resource with optional JSON parsing.

**Parameters:**
- `resource_id` (required): UUID or name of the resource
- `output_format` (optional, default: "raw"):
  - `"raw"` - Returns resource metadata with download URL
  - `"json"` - Downloads and parses resource as JSON

**Example:**
```json
{
  "name": "ckan_resource_download",
  "arguments": {
    "resource_id": "abc123def456",
    "output_format": "json"
  }
}
```

### Enhanced Resource Discovery

- Use `ckan_resource_show` to get detailed resource metadata
- Combine with `ckan_package_search` to find resources by format/criteria
- Use the underlying `RemoteCKAN.session` for direct file downloads

## Implementation Details

### New Files

1. **RESOURCE_DOWNLOAD.md** - Complete documentation and usage guide
2. **example_resource_dump.py** - Practical examples of resource downloading
3. **test_resource_download.py** - Comprehensive test suite

### Modified Files

1. **mcp_ckan_server.py**
   - Added `ckan_resource_download` tool definition in `handle_list_tools()`
   - Added corresponding handler in `handle_call_tool()`
   - Supports both raw and JSON output formats

### Key Features

✅ **Async-aware** - Uses thread pool executor to avoid blocking async code
✅ **Error handling** - Graceful fallback when JSON parsing fails
✅ **Format support** - Works with any resource format (CSV, JSON, XML, etc.)
✅ **Authentication** - Respects API keys and basic auth for protected resources
✅ **Direct session access** - Users can access underlying `requests.Session` for custom operations

## Usage Examples

### Download Resource Metadata
```python
result = await client.call_action("resource_show", id="resource-id")
print(result['url'])  # Download URL
print(result['format'])  # File format
```

### Download and Parse JSON
```python
result = await client.call_action(
    "resource_download",
    resource_id="resource-id",
    output_format="json"
)
data = result['data']  # Parsed JSON array/object
```

### Download Any Format
```python
resource = await client.call_action("resource_show", id="resource-id")
response = client.client.session.get(resource['url'])
with open('downloaded_file', 'wb') as f:
    f.write(response.content)
```

## Testing

All functionality is tested via `test_resource_download.py`:

```bash
uv run python test_resource_download.py
```

Tests include:
- ✅ Getting resource metadata
- ✅ Downloading resources (raw format)
- ✅ Downloading and parsing JSON resources
- ✅ Downloading CSV resources
- ✅ Searching and downloading multiple resources

## Integration with ckanapi

The implementation leverages `ckanapi.RemoteCKAN`:

- **Resource actions** - `resource_show`, `resource_search`
- **Direct session** - `RemoteCKAN.session` for custom requests
- **Error handling** - Proper exception propagation and logging

## Backward Compatibility

✅ All existing MCP tools remain unchanged
✅ No breaking changes to API
✅ New feature is additive only

## Future Enhancements

Possible future additions:
- Batch resource downloads
- Streaming downloads for large files
- Resource format conversion
- Resource caching strategies
- Download progress tracking

## Related Issues

This implementation addresses the use case of downloading resources via the MCP server interface using the `ckanapi` package's dump-like capabilities.

---

**Version**: 1.1.3  
**Date**: 2024-01-15  
**Contributors**: Copilot
