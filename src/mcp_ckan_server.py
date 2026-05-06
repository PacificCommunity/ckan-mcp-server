
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

# Initialize MCP server
app = Server("ckan-mcp-server")

@app.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """List available CKAN API tools"""
    return [
        types.Tool(
            name="ckan_package_list",
            description="Get list of all packages (datasets) in CKAN (unsorted)",
            inputSchema={
                "type": "object",
                "properties": {
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of packages to return",
                        "default": 100
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Offset for pagination",
                        "default": 0
                    }
                }
            }
        ),
        types.Tool(
            name="ckan_package_show",
            description="Get details of a specific package/dataset (like dates)",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Package ID or name"
                    }
                },
                "required": ["id"]
            }
        ),
        types.Tool(
            name="ckan_package_search",
            description="Search for packages using queries",
            inputSchema={
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "Search query",
                        "default": "*:*"
                    },
                    "fq": {
                        "type": "string",
                        "description": "Filter query"
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort field and direction (e.g., 'score desc')"
                    },
                    "rows": {
                        "type": "integer",
                        "description": "Number of results to return",
                        "default": 10
                    },
                    "start": {
                        "type": "integer",
                        "description": "Offset for pagination",
                        "default": 0
                    },
                    "include_private": {
                        "type": "boolean",
                        "description": "Include private packages in search results",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="ckan_organization_list",
            description="Get list of all organizations",
            inputSchema={
                "type": "object",
                "properties": {
                    "all_fields": {
                        "type": "boolean",
                        "description": "Include all organization fields",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="ckan_organization_show",
            description="Get details of a specific organization",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Organization ID or name"
                    },
                    "include_datasets": {
                        "type": "boolean",
                        "description": "Include organization's datasets",
                        "default": False
                    }
                },
                "required": ["id"]
            }
        ),
        types.Tool(
            name="ckan_group_list",
            description="Get list of all groups",
            inputSchema={
                "type": "object",
                "properties": {
                    "all_fields": {
                        "type": "boolean",
                        "description": "Include all group fields",
                        "default": False
                    }
                }
            }
        ),
        types.Tool(
            name="ckan_tag_list",
            description="Get list of all tags",
            inputSchema={
                "type": "object",
                "properties": {
                    "vocabulary_id": {
                        "type": "string",
                        "description": "Vocabulary ID to filter tags"
                    }
                }
            }
        ),
        types.Tool(
            name="ckan_resource_show",
            description="Get details of a specific resource",
            inputSchema={
                "type": "object",
                "properties": {
                    "id": {
                        "type": "string",
                        "description": "Resource ID"
                    }
                },
                "required": ["id"]
            }
        ),
        types.Tool(
            name="ckan_site_read",
            description="Get site information and statistics",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="ckan_status_show",
            description="Get CKAN site status and version information",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),

        types.Tool(
            name="ckan_datastore_search",
            description="Search records in a dataset",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "ID of the resource to search"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results"
                    },
                    "offset": {
                        "type": "integer",
                        "description": "Number of results to skip"
                    },
                    "q": {
                        "type": "string",
                        "description": "Query string in CKAN search syntax"
                    },
                    "sort": {
                        "type": "string",
                        "description": "Sort order e.g. 'field asc'"
                    },
                    "fields": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Fields to return in results"
                    }
                },
                "required": ["resource_id"]
            }
        ),
        types.Tool(
            name="ckan_resource_download",
            description="Download a single resource file from a CKAN instance to disk",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "string",
                        "description": "ID of the resource to download"
                    },
                    "output_folder": {
                        "type": "string",
                        "description": "Local folder path where the resource file will be saved (must exist)"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["raw", "json", "file"],
                        "description": "Output format: 'raw' returns metadata, 'json' parses and returns JSON, 'file' downloads to disk",
                        "default": "file"
                    }
                },
                "required": ["resource_id", "output_folder"]
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
            output_folder = f"{arguments["output_folder"]}"
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
            "client_active": bool(ckan_client and ckan_client.client)
        }
        return json.dumps(config, indent=2)
    else:
        raise Exception(f"Unknown resource: {uri}")
@click.command()
@click.option("--host",default="127.0.0.1", help= "Hostname to listen on for SSE")
@click.option("--port", default=8000, help="Port to listen on for SSE")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "sse"]),
    default="stdio",
    help="Transport type",
)
@click.option("--logpath",default="stderr",help="set path for Logfile")
@click.option("--loglevel",default="INFO",type = click.Choice(logging.getLevelNamesMapping()),help="set Log Level")
def main(host: str,port: int, transport: str,logpath:str,loglevel:str):

    try:
        anyio.run(start_server, host, port, transport, logpath, loglevel)
    except (KeyboardInterrupt, SystemExit):
        pass
async def start_server(host: str,port: int, transport: str,logpath:str,loglevel:str):
    """start_server function"""
    import os
    global logger
    if logpath == "stderr":
        logging.basicConfig(level=loglevel)
    else:
        logging.basicConfig(level=loglevel,filename=logpath)
    logger = logging.getLogger("mcp-ckan-server")
    # Initialize CKAN client
    ckan_url = os.getenv("CKAN_URL")
    if not ckan_url:
        logger.error("CKAN_URL environment variable not set")
        raise Exception("CKAN_URL environment variable is required")

    ckan_api_key = os.getenv("CKAN_API_KEY")
    ckan_basic_auth_username = os.getenv("CKAN_BASIC_AUTH_USERNAME")
    ckan_basic_auth_password = os.getenv("CKAN_BASIC_AUTH_PASSWORD")

    global ckan_client
    ckan_client = CKANAPIClient(ckan_url, ckan_api_key,ckan_basic_auth_username,ckan_basic_auth_password)

    # Start the CKAN client session

    try:
        if transport == "sse":
            from mcp.server.sse import SseServerTransport
            from starlette.applications import Starlette
            from starlette.responses import Response
            from starlette.routing import Mount, Route

            sse = SseServerTransport("/messages/")

            async def handle_sse(request: Request):
                async with sse.connect_sse(request.scope, request.receive, request._send) as streams:  # type: ignore[reportPrivateUsage]
                    if not ckan_client.client:
                            await ckan_client.__aenter__()
                    await app.run(streams[0], streams[1],
                        app.create_initialization_options()
                        )


                    return Response()

            starlette_app = Starlette(
                debug=True,
                routes=[
                    Route("/sse", endpoint=handle_sse, methods=["GET"]),
                    Mount("/messages/", app=sse.handle_post_message),
                ],
            )

            import uvicorn
            config = uvicorn.Config(starlette_app,host=host,port=port)
            server = uvicorn.Server(config)
            await server.serve()
        else:
            from mcp.server.stdio import stdio_server

            async def arun():
                if not ckan_client.client:
                    await ckan_client.__aenter__()
                async with stdio_server() as streams:
                    await app.run(streams[0], streams[1],                 InitializationOptions(
                    server_name="ckan-mcp-server",
                    server_version="1.0.0",
                    capabilities=app.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),)
            await arun()
    finally:
        # Clean up CKAN client
         ckan_client.__aexit__(None, None, None)

if __name__ == "__main__":
    main()
