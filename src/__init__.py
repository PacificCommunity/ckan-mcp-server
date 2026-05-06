"""CKAN MCP Server - Model Context Protocol server for CKAN API"""

__version__ = "1.0.0"
__author__ = "CKAN MCP Contributors"

from .mcp_ckan_server import CKANAPIClient, handle_call_tool

__all__ = [
    "CKANAPIClient",
    "handle_call_tool",
]
