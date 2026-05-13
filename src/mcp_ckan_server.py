
#!/usr/bin/env python3

import asyncio
import anyio
import click
import json
import logging
import os
import pprint
import ssl
import certifi
import tempfile
import io
from typing import Any, Dict, List, Optional, Union
from concurrent.futures import ThreadPoolExecutor
import requests
from ckanapi import RemoteCKAN
from ckanapi.datapackage import create_resource
from mcp.server.models import InitializationOptions
from mcp.server.fastmcp import FastMCP
import mcp.types as types
from mcp.server import NotificationOptions, Server
import mcp.server.stdio
from dotenv import load_dotenv
from starlette.requests import Request

load_dotenv()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

# Initialize logger
logger = logging.getLogger("mcp-ckan-server")
if not logger.handlers:
    logger.addHandler(logging.NullHandler())


class CKANAPIClient:
    """CKAN API client wrapper using ckanapi.RemoteCKAN"""

    def __init__(self, base_url: str, api_key: Optional[str] = None, basic_auth_username: Optional[str] = None, basic_auth_password: Optional[str] = None):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.basic_auth_username = basic_auth_username
        self.basic_auth_password = basic_auth_password
        self.client = None
        self.executor = ThreadPoolExecutor(max_workers=1)

    async def __aenter__(self):
        user_agent = 'MCP-CKAN-Server/1.0 (+http://example.com/mcp-server)'

        # Create a session with proper SSL verification
        session = requests.Session()
        session.verify = certifi.where()

        if self.basic_auth_username and self.basic_auth_password:
            session.auth = (self.basic_auth_username, self.basic_auth_password)

        self.client = RemoteCKAN(
            self.base_url,
            apikey=self.api_key,
            user_agent=user_agent,
            session=session
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.executor:
            self.executor.shutdown(wait=False)

    async def call_action(self, action: str, **kwargs) -> Dict[str, Any]:
        """Call a CKAN action in a thread pool to avoid blocking"""
        def _call():
            action_method = getattr(self.client.action, action)
            return action_method(**kwargs)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(self.executor, _call)
        logger.debug(f"CKAN action '{action}' result: {result}")
        return result

# Global CKAN client
ckan_client = None


async def get_ckan_client() -> CKANAPIClient:
    """Initialize the shared CKAN client from environment variables."""
    global ckan_client
    if ckan_client and ckan_client.client:
        return ckan_client

    ckan_url = os.getenv("CKAN_URL")
    if not ckan_url:
        raise Exception("CKAN_URL environment variable is required")

    ckan_client = CKANAPIClient(
        ckan_url,
        os.getenv("CKAN_API_KEY"),
        os.getenv("CKAN_BASIC_AUTH_USERNAME"),
        os.getenv("CKAN_BASIC_AUTH_PASSWORD"),
    )
    await ckan_client.__aenter__()
    return ckan_client

# Initialize MCP server
app = Server("ckan-mcp-server")

@app.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available CKAN API tools organized by capability"""
    return [
        # === DATA DISCOVERY & SEARCH ===
        types.Tool(
            name="ckan_package_search",
            description="Search datasets by keywords, themes, tags, or custom filters. Use this to find specific datasets by content, date range, organization, or metadata. Perfect for exploring public datasets or discovering resources within your CKAN portal.",
            inputSchema={
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "Search query (e.g., 'climate', 'budget', '*:*' for all). Use keywords that match dataset titles or descriptions.",
                        "default": "*:*"
                    },
                    "fq": {
                        "type": "string",
                        "description": "Advanced filter (e.g., 'organization:health-dept', 'res_format:CSV'). Filters results without affecting relevance ranking."
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort results (e.g., 'score desc' for relevance, 'metadata_modified desc' for newest first)",
                        "default": "score desc"
                    },
                    "rows": {
                        "type": "integer",
                        "description": "Number of results per page (max 1000)",
                        "default": 10
                    },
                    "start": {
                        "type": "integer",
                        "description": "Pagination offset (skip N results)",
                        "default": 0
                    },
                    "include_private": {
                        "type": "boolean",
                        "description": "Include private/restricted datasets (requires appropriate permissions)",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="ckan_package_list",
            description="Browse all datasets in the portal by listing them with pagination. Use when you need a simple list of all available datasets without searching, or for data inventory/governance tasks.",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Number of datasets to return per request",
                        "default": 100
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Skip N datasets (for pagination)",
                        "default": 0
                    }
                }
            }
        ),
        types.Tool(
            name="ckan_package_show",
            description="Retrieve complete details for a specific dataset including metadata, resources, creation/update dates, maintainer info, and linked data. Use when you need full information about a known dataset.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Dataset ID or name (e.g., 'covid-19-statistics' or '12345-67890')"
                    }
                },
                "required": ["id"]
            }
        ),

        # === DATA ACCESS & RETRIEVAL ===
        types.Tool(
            name="ckan_datastore_search",
            description="Query and retrieve actual data records from structured table resources. Use to access tabular data, apply filters, sort results, and analyze datasets without downloading.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "ID of the DataStore resource (typically a CSV or database-backed resource)"
                    },
                    "q": {
                        "type": "string",
                        "description": "Full-text search query to filter records by content"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum records to return (default/max varies by CKAN config)",
                        "default": 100
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Skip N records (for pagination through large datasets)",
                        "default": 0
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort results (e.g., 'date desc', 'name asc'). Specify column name and direction.",
                        "default": "id asc"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Specific columns to retrieve (e.g., ['date', 'value', 'location']). Omit to get all fields."
                    }
                },
                "required": ["resource_id"]
            }
        ),
        types.Tool(
            name="ckan_resource_show",
            description="Get metadata for a specific file or data resource within a dataset (URL, format, size, creation date, etc.). Use before downloading to check resource properties.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Resource ID (UUID or identifier)"
                    }
                },
                "required": ["id"]
            }
        ),
        types.Tool(
            name="ckan_resource_download",
            description="Download a dataset resource file to your local system. Supports CSV, JSON, Excel, and other formats with automatic format detection. Perfect for local analysis or archival.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "ID of the resource to download"
                    },
                    "output_folder": {
                        "type": "string",
                        "description": "Local folder path where file will be saved (folder must already exist)"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["raw", "json", "file"],
                        "description": "'raw' = metadata only, 'json' = parse and return as JSON, 'file' = save to disk",
                        "default": "file"
                    }
                },
                "required": ["resource_id", "output_folder"]
            }
        ),

        # === ORGANIZATION & STRUCTURE ===
        types.Tool(
            name="ckan_organization_list",
            description="List all data-publishing organizations in your portal. Use for organizational hierarchy discovery, reporting, or to identify which team manages specific datasets.",
            inputSchema={
                "type": "object",
                "properties": {
                    "all_fields": {
                        "type": "boolean",
                        "description": "Include all organization details (description, image, creation date, member count, etc.). Set true for comprehensive reporting.",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="ckan_organization_show",
            description="Get full details for a specific organization including description, members, contact info, and optionally all their published datasets. Use for organizational reports or understanding data stewardship.",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Organization ID or name (e.g., 'health-department')"
                    },
                    "include_datasets": {
                        "type": "boolean",
                        "description": "Include all datasets published by this organization (useful for org-specific analysis)",
                        "default": False
                    }
                },
                "required": ["id"]
            }
        ),
        types.Tool(
            name="ckan_group_list",
            description="List all groups in the portal. Groups are like categories or themes for organizing datasets. Use to explore data taxonomy and themed collections.",
            inputSchema={
                "type": "object",
                "properties": {
                    "all_fields": {
                        "type": "boolean",
                        "description": "Include group descriptions, image, creation date. Set true for detailed catalog browsing.",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="ckan_tag_list",
            description="List all metadata tags/keywords used in the portal. Use to understand available tags, discover tagging conventions, or filter searches by tag vocabulary.",
            inputSchema={
                "type": "object",
                "properties": {
                    "vocabulary_id": {
                        "type": "string",
                        "description": "Filter to a specific vocabulary/controlled list (optional). Use for custom tag systems like geographic locations or departments."
                    }
                }
            }
        ),

        # === SYSTEM & STATUS ===
        types.Tool(
            name="ckan_site_read",
            description="Get overall CKAN portal information including site title, description, organization count, dataset count, and other aggregate statistics. Use for portal health checks or metadata.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="ckan_status_show",
            description="Check CKAN system status and version. Useful for verifying API availability, version compatibility, and operational monitoring.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        # @TODO Untested
        # types.Tool(
        #     name="ckan_datastore_create",
        #     description="Create an empty dataset in the datastore",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "resource_id": {
        #                 "type": "string",
        #                 "description": "ID of the resource to create"
        #             },
        #             "table_name": {
        #                 "type": "string",
        #                 "description": "Optional table name"
        #             },
        #             "schema": {
        #                 "type": "object",
        #                 "description": "Schema definition for the dataset"
        #             }
        #         },
        #         "required": ["resource_id"]
        #     }
        # ),
        # types.Tool(
        #     name="ckan_datastore_upsert",
        #     description="Insert or update rows in a datastore table",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "resource_id": {
        #                 "type": "string",
        #                 "description": "ID of the resource to upsert"
        #             },
        #             "records": {
        #                 "type": "array",
        #                 "items": {"type": "object","properties": {}},
        #                 "description": "List of records to upsert"
        #             },
        #             "method": {
        #                 "type": "string",
        #                 "enum": ["insert", "update", "upsert"],
        #                 "description": "Method to use"
        #             }
        #         },
        #         "required": ["resource_id", "records", "method"]
        #     }
        # ),
        # types.Tool(
        #     name="ckan_datastore_delete",
        #     description="Delete rows from a datastore table",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "resource_id": {
        #                 "type": "string",
        #                 "description": "ID of the resource to delete from"
        #             },
        #             "ids": {
        #                 "type": "array",
        #                 "items": {"type": "string"},
        #                 "description": "List of record IDs to delete"
        #             }
        #         },
        #         "required": ["resource_id", "ids"]
        #     }
        # ),
        # types.Tool(
        #     name="ckan_datastore_commit",
        #     description="Commit changes to a datastore table",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "resource_id": {
        #                 "type": "string",
        #                 "description": "ID of the resource to commit"
        #             }
        #         },
        #         "required": ["resource_id"]
        #     }
        # ),
        # types.Tool(
        #     name="ckan_datastore_table_create",
        #     description="Create a datastore table",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "resource_id": {
        #                 "type": "string",
        #                 "description": "ID of the resource"
        #             },
        #             "schema": {
        #                 "type": "object",
        #                 "description": "Schema definition"
        #             }
        #         },
        #         "required": ["resource_id", "schema"]
        #     }
        # ),
        # types.Tool(
        #     name="ckan_datastore_table_delete",
        #     description="Delete a datastore table",
        #     inputSchema={
        #         "type": "object",
        #         "properties": {
        #             "resource_id": {
        #                 "type": "string",
        #                 "description": "ID of the resource to delete"
        #             }
        #         },
        #         "required": ["resource_id"]
        #     }
        # ),

    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[types.TextContent]:
    """Handle tool calls to CKAN API"""
    if not ckan_client:
        raise Exception("CKAN client not initialized. Please set CKAN_URL environment variable.")

    try:
        if name == "ckan_package_list":
            limit = arguments.get("limit", 100) if arguments else 100
            offset = arguments.get("offset", 0) if arguments else 0
            result = await ckan_client.call_action("package_list", limit=limit, offset=offset)

        elif name == "ckan_package_show":
            package_id = arguments["id"]
            result = await ckan_client.call_action("package_show", id=package_id)

        elif name == "ckan_package_search":
            params = arguments or {}
            if params.get("include_private", False) and not (
                os.getenv("CKAN_BASIC_AUTH_USERNAME") and os.getenv("CKAN_BASIC_AUTH_PASSWORD")
            ):
                raise Exception(
                    "Feature 'include_private' requires CKAN_BASIC_AUTH_USERNAME and CKAN_BASIC_AUTH_PASSWORD to be configured."
                )
            result = await ckan_client.call_action("package_search", **params)

        elif name == "ckan_organization_list":
            all_fields = arguments.get("all_fields", False) if arguments else False
            result = await ckan_client.call_action("organization_list", all_fields=all_fields)

        elif name == "ckan_organization_show":
            org_id = arguments["id"]
            include_datasets = arguments.get("include_datasets", False)
            result = await ckan_client.call_action("organization_show", id=org_id, include_datasets=include_datasets)

        elif name == "ckan_group_list":
            all_fields = arguments.get("all_fields", False) if arguments else False
            result = await ckan_client.call_action("group_list", all_fields=all_fields)

        elif name == "ckan_tag_list":
            params = arguments or {}
            result = await ckan_client.call_action("tag_list", **params)

        elif name == "ckan_resource_show":
            resource_id = arguments["id"]
            result = await ckan_client.call_action("resource_show", id=resource_id)

        elif name == "ckan_site_read":
            result = await ckan_client.call_action("site_read")

        elif name == "ckan_status_show":
            result = await ckan_client.call_action("status_show")

        elif name == "ckan_datastore_search":
            result = await ckan_client.call_action("datastore_search", **arguments)

        elif name == "ckan_resource_download":
            resource_id = arguments["resource_id"]
            output_folder = str(arguments["output_folder"])
            output_format = arguments.get("output_format", "file")

            # Validate output_folder exists
            if not os.path.isdir(output_folder):
                raise Exception(f"Output folder does not exist: {output_folder}")

            # Get resource metadata
            result = await ckan_client.call_action("resource_show", id=resource_id)

            if output_format == "raw":
                # Return metadata with download URL
                pass

            elif output_format == "file":
                # Download to disk using ckanapi's create_resource function
                def _download_file():
                    import shutil
                    # Get filename from resource name or fallback to resource_id
                    base_filename = result.get("name", f"resource_{resource_id}")

                    # Get file extension from mimetype or format
                    import mimetypes
                    extension = ""

                    # Try mimetype first
                    mimetype = result.get("mimetype", "")
                    if mimetype:
                        ext = mimetypes.guess_extension(mimetype)
                        if ext:
                            extension = ext.lstrip(".")

                    # Fallback to format field
                    if not extension:
                        extension = result.get("format", "").lower()

                    # Build final filename
                    if extension and not base_filename.endswith(f".{extension}"):
                        filename = f"{base_filename}.{extension}"
                    else:
                        filename = base_filename

                    stderr_buffer = io.StringIO()

                    try:
                        # Ensure data subfolder exists (create_resource requires it)
                        data_dir = os.path.join(output_folder, "data")
                        os.makedirs(data_dir, exist_ok=True)
                        
                        # Use ckanapi.datapackage.create_resource to download
                        # Note: create_resource saves to datapackage_dir/data/filename
                        downloaded_resource = create_resource(
                            resource=result,
                            filename=filename,
                            datapackage_dir=output_folder,
                            stderr=stderr_buffer,
                            apikey=ckan_client.api_key or ""
                        )

                        # create_resource saves to output_folder/data/filename
                        temp_file_path = os.path.join(output_folder, "data", filename)
                        final_file_path = os.path.join(output_folder, filename)

                        if os.path.exists(temp_file_path):
                            # Move file from data/ subfolder to output_folder root
                            shutil.move(temp_file_path, final_file_path)

                            file_size = os.path.getsize(final_file_path)

                            return {
                                "status": "success",
                                "resource_id": resource_id,
                                "filename": filename,
                                "file_path": final_file_path,
                                "size": file_size,
                                "format": result.get("format", "unknown"),
                                "url": result.get("url"),
                                "message": f"File downloaded successfully to {final_file_path} ({file_size} bytes)"
                            }
                        else:
                            stderr_msg = stderr_buffer.getvalue()
                            return {
                                "status": "error",
                                "message": f"Downloaded file not found at {temp_file_path}",
                                "stderr": stderr_msg if stderr_msg else "(no error details)"
                            }
                    except Exception as e:
                        return {
                            "status": "error",
                            "message": str(e),
                            "stderr": stderr_buffer.getvalue()
                        }

                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(ckan_client.executor, _download_file)

            elif output_format == "json":
                # Download and parse JSON resource
                resource_url = result.get("url")
                if not resource_url:
                    raise Exception("Resource has no URL")

                # Download the resource using requests
                response = ckan_client.client.session.get(resource_url)
                response.raise_for_status()

                try:
                    result = {
                        "resource_metadata": result,
                        "data": response.json()
                    }
                except ValueError:
                    result = {
                        "resource_metadata": result,
                        "data": response.text,
                        "format_note": "Resource was not valid JSON, returning as text"
                    }
            # For "raw" format, just return the resource metadata with download URL

        # @TODO: untested
        # elif name == "ckan_datastore_create":
        #     result = await ckan_client.call_action("datastore_create", **arguments)
        # elif name == "ckan_datastore_update":
        #     result = await ckan_client.call_action("datastore_update", **arguments)
        # elif name == "ckan_datastore_upsert":
        #     result = await ckan_client.call_action("datastore_upsert", **arguments)
        # elif name == "ckan_datastore_delete":
        #     result = await ckan_client.call_action("datastore_delete", **arguments)


        else:
            raise Exception(f"Unknown tool: {name}")

        return [
            types.TextContent(
                type="text",
                text=json.dumps(result, indent=2, ensure_ascii=False)
            )
        ]

    except Exception as e:
        logger.error(f"Error calling tool {name}: {str(e)}")
        return [
            types.TextContent(
                type="text",
                text=f"Error: {str(e)}"
            )
        ]

@app.list_resources()
async def handle_list_resources() -> List[types.Resource]:
    """List available CKAN resources"""
    return [
        types.Resource(
            uri="ckan://api/docs",
            name="CKAN API Documentation",
            description="Official CKAN API documentation and endpoints",
            mimeType="text/plain"
        ),
        types.Resource(
            uri="ckan://config",
            name="CKAN Server Configuration",
            description="Current CKAN server configuration and connection details",
            mimeType="application/json"
        )
    ]

@app.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Read CKAN resources"""
    if uri == "ckan://api/docs":
        return """
CKAN API Documentation Summary

Base URL: Configure via CKAN_URL environment variable
API Version: 3

Key Endpoints:
- package_list: Get all packages/datasets
- package_show: Get package details
- package_search: Search packages
- organization_list: Get all organizations
- organization_show: Get organization details
- group_list: Get all groups
- tag_list: Get all tags
- resource_show: Get resource details
- site_read: Get site information
- status_show: Get site status

Authentication: Set CKAN_API_KEY environment variable for write operations

Full documentation: https://docs.ckan.org/en/latest/api/
        """
    elif uri == "ckan://config":
        config = {
            "base_url": ckan_client.base_url if ckan_client else "Not configured",
            "api_key_configured": bool(ckan_client and ckan_client.api_key),
            "basic_auth_configured": bool(
                os.getenv("CKAN_BASIC_AUTH_USERNAME") and os.getenv("CKAN_BASIC_AUTH_PASSWORD")
            ),
            "unavailable_features": []
            if os.getenv("CKAN_BASIC_AUTH_USERNAME") and os.getenv("CKAN_BASIC_AUTH_PASSWORD")
            else ["include_private"],
            "client_active": bool(ckan_client and ckan_client.client)
        }
        return json.dumps(config, indent=2)
    else:
        raise Exception(f"Unknown resource: {uri}")
def _extract_tool_result(result_content: list[types.TextContent]) -> Any:
    if not result_content:
        return {}
    text = result_content[0].text
    if text.startswith("Error: "):
        raise Exception(text.removeprefix("Error: "))
    return json.loads(text)


fastmcp_app = FastMCP("ckan-mcp-server")


def register_fastmcp_tools(mcp_app: FastMCP) -> None:
    @mcp_app.tool(name="ckan_package_search", description="Search datasets by keywords, filters, and pagination.")
    async def ckan_package_search(
        q: str = "*:*",
        fq: Optional[str] = None,
        sort: str = "score desc",
        rows: int = 10,
        start: int = 0,
        include_private: bool = False,
    ) -> dict[str, Any]:
        return _extract_tool_result(
            await handle_call_tool(
                "ckan_package_search",
                {
                    "q": q,
                    "fq": fq,
                    "sort": sort,
                    "rows": rows,
                    "start": start,
                    "include_private": include_private,
                },
            )
        )

    @mcp_app.tool(name="ckan_package_list", description="List datasets with pagination.")
    async def ckan_package_list(limit: int = 100, offset: int = 0) -> dict[str, Any]:
        return _extract_tool_result(await handle_call_tool("ckan_package_list", {"limit": limit, "offset": offset}))

    @mcp_app.tool(name="ckan_package_show", description="Get full metadata for a dataset.")
    async def ckan_package_show(id: str) -> dict[str, Any]:
        return _extract_tool_result(await handle_call_tool("ckan_package_show", {"id": id}))

    @mcp_app.tool(name="ckan_datastore_search", description="Search rows in a DataStore resource.")
    async def ckan_datastore_search(
        resource_id: str,
        q: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
        sort: str = "id asc",
        fields: Optional[list[str]] = None,
    ) -> dict[str, Any]:
        args: dict[str, Any] = {"resource_id": resource_id, "limit": limit, "offset": offset, "sort": sort}
        if q:
            args["q"] = q
        if fields:
            args["fields"] = fields
        return _extract_tool_result(await handle_call_tool("ckan_datastore_search", args))

    @mcp_app.tool(name="ckan_resource_show", description="Get metadata for a CKAN resource.")
    async def ckan_resource_show(id: str) -> dict[str, Any]:
        return _extract_tool_result(await handle_call_tool("ckan_resource_show", {"id": id}))

    @mcp_app.tool(
        name="ckan_resource_download",
        description="Download resource metadata, JSON content, or file to disk.",
    )
    async def ckan_resource_download(
        resource_id: str,
        output_folder: str,
        output_format: str = "file",
    ) -> dict[str, Any]:
        return _extract_tool_result(
            await handle_call_tool(
                "ckan_resource_download",
                {
                    "resource_id": resource_id,
                    "output_folder": output_folder,
                    "output_format": output_format,
                },
            )
        )

    @mcp_app.tool(name="ckan_organization_list", description="List CKAN organizations.")
    async def ckan_organization_list(all_fields: bool = False) -> dict[str, Any]:
        return _extract_tool_result(await handle_call_tool("ckan_organization_list", {"all_fields": all_fields}))

    @mcp_app.tool(name="ckan_organization_show", description="Get organization details.")
    async def ckan_organization_show(id: str, include_datasets: bool = False) -> dict[str, Any]:
        return _extract_tool_result(
            await handle_call_tool("ckan_organization_show", {"id": id, "include_datasets": include_datasets})
        )

    @mcp_app.tool(name="ckan_group_list", description="List CKAN groups.")
    async def ckan_group_list(all_fields: bool = False) -> dict[str, Any]:
        return _extract_tool_result(await handle_call_tool("ckan_group_list", {"all_fields": all_fields}))

    @mcp_app.tool(name="ckan_tag_list", description="List CKAN tags.")
    async def ckan_tag_list(vocabulary_id: Optional[str] = None) -> dict[str, Any]:
        args: dict[str, Any] = {}
        if vocabulary_id:
            args["vocabulary_id"] = vocabulary_id
        return _extract_tool_result(await handle_call_tool("ckan_tag_list", args))

    @mcp_app.tool(name="ckan_site_read", description="Get CKAN site summary details.")
    async def ckan_site_read() -> dict[str, Any]:
        return _extract_tool_result(await handle_call_tool("ckan_site_read", {}))

    @mcp_app.tool(name="ckan_status_show", description="Get CKAN system status.")
    async def ckan_status_show() -> dict[str, Any]:
        return _extract_tool_result(await handle_call_tool("ckan_status_show", {}))


def register_fastmcp_resources(mcp_app: FastMCP) -> None:
    @mcp_app.resource(
        "ckan://api/docs",
        name="CKAN API Documentation",
        description="Official CKAN API documentation and endpoints",
        mime_type="text/plain",
    )
    def ckan_api_docs() -> str:
        return """
CKAN API Documentation Summary

Base URL: Configure via CKAN_URL environment variable
API Version: 3
        """

    @mcp_app.resource(
        "ckan://config",
        name="CKAN Server Configuration",
        description="Current CKAN server configuration and connection details",
        mime_type="application/json",
    )
    def ckan_config() -> str:
        auth_configured = bool(os.getenv("CKAN_BASIC_AUTH_USERNAME") and os.getenv("CKAN_BASIC_AUTH_PASSWORD"))
        config = {
            "base_url": _ckan_client.base_url if _ckan_client else os.getenv("CKAN_URL", "Not configured"),
            "api_key_configured": bool((_ckan_client and _ckan_client.api_key) or os.getenv("CKAN_API_KEY")),
            "basic_auth_configured": auth_configured,
            "unavailable_features": [] if auth_configured else ["include_private"],
            "client_active": bool(_ckan_client and _ckan_client.client),
        }
        return json.dumps(config, indent=2)


register_fastmcp_tools(fastmcp_app)
register_fastmcp_resources(fastmcp_app)


async def run_server(host: str, port: int, transport: str, logpath: str, loglevel: str) -> None:
    global logger, ckan_client

    if logpath == "stderr":
        logging.basicConfig(level=loglevel)
    else:
        logging.basicConfig(level=loglevel, filename=logpath)

    logger = logging.getLogger("mcp-ckan-server")

    ckan_url = os.getenv("CKAN_URL")
    if not ckan_url:
        logger.error("CKAN_URL environment variable not set")
        raise Exception("CKAN_URL environment variable is required")

    ckan_client = await get_ckan_client()
    logger.info("CKAN MCP Server is up and running (%s transport). Connected to %s", transport, ckan_url)

    fastmcp_app.settings.host = host
    fastmcp_app.settings.port = port
    fastmcp_app.settings.log_level = loglevel

    try:
        if transport == "stdio":
            await fastmcp_app.run_stdio_async()
        elif transport == "streamable-http":
            await fastmcp_app.run_streamable_http_async()
        else:
            raise Exception(f"Unsupported transport: {transport}")
    finally:
        if ckan_client:
            await ckan_client.__aexit__(None, None, None)
            ckan_client = None


@click.command()
@click.option("--host", default="127.0.0.1", help="Hostname to listen on")
@click.option("--port", default=8000, help="Port to listen on")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "streamable-http"]),
    default="stdio",
    help="Transport type",
)
@click.option("--logpath", default="stderr", help="Path for logfile")
@click.option("--loglevel", default="INFO", type=click.Choice(list(logging.getLevelNamesMapping().keys())), help="Log level")
def main(host: str, port: int, transport: str, logpath: str, loglevel: str) -> None:
    try:
        anyio.run(run_server, host, port, transport, logpath, loglevel)
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    main()
