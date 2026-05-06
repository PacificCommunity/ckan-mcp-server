# Tests

Test suite for the CKAN MCP Server.

## Files

- **test_resource_download.py** - Unit tests for resource download functionality
  - Mock-based tests for all output formats (raw, json, file)
  - Error handling verification
  - No network required

- **test_download_pacificdata.py** - Integration test with real CKAN instance
  - Tests against live Pacific Data CKAN instance
  - Full end-to-end MCP tool testing
  - Requires .env configuration

## Running Tests

### Unit Tests (No Network Required)

```bash
# Run all unit tests
pytest tests/test_resource_download.py -v

# Run specific test
pytest tests/test_resource_download.py::test_resource_download_file -v

# Run with coverage
pytest tests/ --cov=src/
```

### Integration Tests (Requires CKAN Instance)

```bash
# Setup .env file
cp .env.sample .env
# Edit .env with:
# CKAN_URL=https://pacificdata.org/data
# CKAN_API_KEY=your-key

# Run integration test
python tests/test_download_pacificdata.py
```

## Test Coverage

Current test coverage includes:

- ✅ Resource metadata retrieval
- ✅ Raw format downloads
- ✅ JSON parsing and fallback
- ✅ CSV format handling
- ✅ File format with create_resource
- ✅ Error handling
- ✅ MCP tool dispatcher
- ✅ Authentication

## Adding New Tests

### Unit Test Template

```python
async def test_new_feature():
    """Test description"""
    client = CKANAPIClient('https://demo.ckan.org', api_key='test-key')
    
    async with client as c:
        # Mock the action
        c.client.action.resource_show = Mock(return_value={
            'id': 'test-123',
            'name': 'Test Resource',
            'format': 'CSV',
            'url': 'https://example.com/data.csv'
        })
        
        # Call action
        result = await client.call_action("resource_show", id='test-123')
        
        # Assert
        assert result['name'] == 'Test Resource'
```

### Integration Test Template

```python
async def test_real_ckan_instance():
    """Test against real CKAN instance"""
    load_dotenv()
    
    ckan_url = os.getenv("CKAN_URL")
    api_key = os.getenv("CKAN_API_KEY")
    
    client = CKANAPIClient(ckan_url, api_key=api_key)
    
    async with client as c:
        result = await client.call_action("package_list", limit=1)
        assert result is not None
```

## CI/CD Integration

Tests are designed to run in CI/CD pipelines:

- Unit tests run on every commit (no external dependencies)
- Integration tests run on PR (requires test CKAN instance)
- Coverage reports generated automatically

## Troubleshooting

### Tests fail with connection errors
- Check .env configuration
- Verify CKAN instance is accessible
- Check API key validity

### Mock-related import errors
- Ensure unittest.mock is available (built-in for Python 3.3+)
- Update test imports if needed

### Async test issues
- Use `pytest-asyncio` plugin
- Mark async tests with `@pytest.mark.asyncio`
