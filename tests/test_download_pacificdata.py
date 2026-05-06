#!/usr/bin/env python3
"""
Test the resource download feature with Pacific Data instance
Uses the ckan_resource_download MCP tool to download resources
"""

import asyncio
import sys
import os
import json
import tempfile
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(__file__))

async def test_download_pacificdata():
    """Download resource from Pacific Data CKAN instance using MCP tool"""

    # Load environment variables from .env
    load_dotenv()

    ckan_url = os.getenv("CKAN_URL")
    api_key = os.getenv("CKAN_API_KEY")

    # Resource ID hardcoded in script
    resource_id = "17b39833-1d29-4d89-ac1a-55c536ada7a4"

    if not ckan_url:
        print("❌ Error: CKAN_URL not set in .env file")
        sys.exit(1)
    if not api_key:
        print("❌ Error: CKAN_API_KEY not set in .env file")
        sys.exit(1)

    # Create output folder
    output_folder = tempfile.mkdtemp()
    output_folder = "."

    print(f"🔗 Connecting to CKAN instance: {ckan_url}")
    print(f"📦 Resource ID: {resource_id}")
    print(f"📁 Output folder: {output_folder}\n")

    # Import server components
    import mcp_ckan_server
    import mcp.types as types

    # Initialize the global ckan_client in the module
    mcp_ckan_server.ckan_client = mcp_ckan_server.CKANAPIClient(ckan_url, api_key=api_key)

    try:
        async with mcp_ckan_server.ckan_client as client:
            # Step 1: Get resource metadata
            print("Step 1: Fetching resource metadata...")
            try:
                resource = await mcp_ckan_server.ckan_client.call_action("resource_show", id=resource_id)
                print(f"✓ Resource found: {resource.get('name', 'N/A')}")
                print(f"  Format: {resource.get('format', 'N/A')}")
                print(f"  Mimetype: {resource.get('mimetype', 'N/A')}")
                print(f"  URL: {resource.get('url', 'N/A')}")
                print(f"  Size: {resource.get('size', 'N/A')} bytes")
            except Exception as e:
                print(f"✗ Error fetching resource: {e}")
                return

            # Step 2: Call the ckan_resource_download MCP tool
            print("\nStep 2: Calling ckan_resource_download MCP tool...")
            try:
                # Prepare tool arguments
                arguments = {
                    "resource_id": resource_id,
                    "output_folder": output_folder,
                    "output_format": "file"
                }

                print(f"  Tool arguments:")
                for key, value in arguments.items():
                    print(f"    {key}: {value}")
                print(f"  Downloading...")

                # Call the MCP tool handler
                result_content = await mcp_ckan_server.handle_call_tool("ckan_resource_download", arguments)

                # Parse result (should be a list of TextContent)
                if isinstance(result_content, list) and len(result_content) > 0:
                    result_text = result_content[0].text
                else:
                    result_text = str(result_content)

                print(result_text)
                result_data = json.loads(result_text)

                print(f"\n✓ Tool execution result:")
                print(f"  Status: {result_data.get('status', 'unknown')}")

                if result_data.get('status') == 'success':
                    print(f"  File: {result_data.get('filename')}")
                    print(f"  Path: {result_data.get('file_path')}")
                    print(f"  Size: {result_data.get('size')} bytes")
                    print(f"  Format: {result_data.get('format')}")
                    print(f"  Message: {result_data.get('message')}")

                    # Verify file exists
                    file_path = result_data.get('file_path')
                    if os.path.exists(file_path):
                        print(f"  ✓ File verified at: {file_path}")

                        # Show preview for text files
                        extension = os.path.splitext(file_path)[1].lower()
                        if extension in ['.csv', '.json', '.txt', '.geojson']:
                            try:
                                with open(file_path, 'rb') as f:
                                    preview = f.read(500).decode('utf-8', errors='ignore')
                                print(f"  Preview:\n{preview}...")
                            except:
                                pass
                    else:
                        print(f"  ✗ File not found at: {file_path}")
                else:
                    print(f"  Error: {result_data.get('message')}")
                    if result_data.get('stderr'):
                        print(f"  Stderr: {result_data.get('stderr')}")

            except Exception as e:
                print(f"✗ Error calling tool: {e}")
                import traceback
                traceback.print_exc()

    finally:
        # Cleanup
        print(f"\nCleaning up temp directory: {output_folder}")
        #import shutil
        #shutil.rmtree(output_folder, ignore_errors=True)

if __name__ == "__main__":
    asyncio.run(test_download_pacificdata())
