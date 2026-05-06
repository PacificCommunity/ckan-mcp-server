# Contributing to CKAN MCP Server

Thank you for your interest in contributing! This document outlines how to get started.

## Project Structure

```
ckan-mcp-server/
├── src/                      # Main source code
│   ├── mcp_ckan_server.py   # MCP server implementation
│   └── __init__.py
├── tests/                    # Test suite
│   ├── test_resource_download.py
│   └── test_download_pacificdata.py
├── examples/                 # Usage examples
│   ├── example_resource_dump.py
│   └── test_download_pacificdata.py
├── docs/                     # Documentation
│   ├── RESOURCE_DOWNLOAD.md
│   └── README.md
├── pyproject.toml            # Project metadata
├── Makefile                  # Build tasks
└── Dockerfile               # Container definition
```

## Development Setup

### Prerequisites

- Python 3.13+
- uv (package manager)
- Git

### Local Installation

```bash
# Clone the repository
git clone https://github.com/ondics/ckan-mcp-server.git
cd ckan-mcp-server

# Create virtual environment
uv venv

# Activate (on Linux/macOS)
source .venv/bin/activate
# or on Windows
.venv\Scripts\activate

# Install in development mode
uv pip install -e ".[dev]"
```

### Configuration

```bash
# Copy sample environment file
cp .env.sample .env

# Edit with your CKAN instance details
CKAN_URL=https://your-instance.org
CKAN_API_KEY=your-key
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or for bugs:
git checkout -b fix/your-bug-fix
```

### 2. Make Your Changes

#### Adding a New MCP Tool

1. Add tool definition in `handle_list_tools()` (around line 200)
2. Add handler in `handle_call_tool()` (around line 426)
3. Add unit tests in `tests/test_*.py`
4. Update documentation

Example:

```python
# In handle_list_tools()
types.Tool(
    name="ckan_my_new_tool",
    description="My new tool description",
    inputSchema={
        "type": "object",
        "properties": {
            "param": {
                "type": "string",
                "description": "Parameter description"
            }
        },
        "required": ["param"]
    }
)

# In handle_call_tool()
elif name == "ckan_my_new_tool":
    param = arguments.get("param")
    result = await ckan_client.call_action("my_action", param=param)
```

### 3. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_resource_download.py::test_resource_download_file -v

# Run with coverage
pytest tests/ --cov=src/ --cov-report=html

# Integration tests
python tests/test_download_pacificdata.py
```

### 4. Verify Code Quality

```bash
# Format code
black src/ tests/ examples/

# Lint
flake8 src/ tests/ examples/

# Type checking (if available)
mypy src/
```

### 5. Commit Your Changes

```bash
git add .
git commit -m "feat: add new feature

Longer description of changes if needed.

Fixes #123"
```

**Commit message format:**
- `feat:` for new features
- `fix:` for bug fixes
- `docs:` for documentation
- `test:` for tests
- `refactor:` for code refactoring
- `chore:` for maintenance

### 6. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then open a Pull Request on GitHub with:
- Clear description of changes
- Reference to related issues
- Screenshots if UI changes
- Test results

## Code Style Guidelines

### Python

- Follow PEP 8 (use black for formatting)
- Use type hints where possible
- Write descriptive docstrings
- Keep functions focused and small

### Async Code

All I/O operations should be async:

```python
# Good
async def fetch_data():
    result = await client.call_action("package_search")
    return result

# Avoid
def fetch_data():
    # Don't block the event loop
    result = ckan_client.sync_action("package_search")
```

### Error Handling

```python
# Good - specific exception handling
try:
    result = await client.call_action("action")
except requests.ConnectionError as e:
    logger.error(f"Connection failed: {e}")
    raise Exception(f"Failed to connect to CKAN: {e}")

# Avoid - bare except
try:
    result = await client.call_action("action")
except:
    pass
```

## Testing

### Writing Tests

- Place tests in `tests/` directory
- Use descriptive test names: `test_<feature>_<scenario>`
- Mock external dependencies
- Test both success and error cases

Example:

```python
async def test_resource_download_success():
    """Test successful resource download"""
    client = CKANAPIClient('https://demo.ckan.org', api_key='key')
    
    async with client as c:
        # Mock response
        c.client.action.resource_show = Mock(return_value={
            'id': 'test-123',
            'name': 'Test Resource',
            'format': 'CSV',
            'url': 'https://example.com/data.csv'
        })
        
        # Test
        result = await client.call_action("resource_show", id='test-123')
        
        # Assert
        assert result['id'] == 'test-123'
        assert result['format'] == 'CSV'
```

### Running Tests Locally

```bash
# All tests
pytest

# Verbose output
pytest -v

# Stop on first failure
pytest -x

# Show print statements
pytest -s

# Specific file
pytest tests/test_resource_download.py

# Specific test
pytest tests/test_resource_download.py::test_name
```

## Documentation

### Docstrings

Use Google-style docstrings:

```python
async def call_action(self, action: str, **kwargs) -> Dict[str, Any]:
    """Call a CKAN API action.
    
    Args:
        action: Name of the CKAN action to call
        **kwargs: Arguments to pass to the action
        
    Returns:
        The result data from the action
        
    Raises:
        Exception: If action fails or CKAN returns error
        
    Example:
        >>> result = await client.call_action("package_list", limit=10)
    """
```

### Markdown Files

- Use clear headings
- Include code examples
- Add links to related docs
- Keep line length reasonable

## Release Process

1. Update version in `pyproject.toml`
2. Update `CHANGELOG.md`
3. Tag release: `git tag v1.x.x`
4. Push tags: `git push origin --tags`
5. Create GitHub release

## Getting Help

- **Issues**: Open a GitHub issue for bugs or feature requests
- **Discussions**: Use GitHub Discussions for questions
- **Email**: Contact info@ondics.de
- **Documentation**: Check `docs/` folder

## Code of Conduct

- Be respectful and inclusive
- Provide constructive feedback
- Respect intellectual property
- Report security issues responsibly

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

Thank you for contributing! 🙏
