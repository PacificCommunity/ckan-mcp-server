#!/usr/bin/env python3
"""
Example: Download single resources from CKAN using ckanapi
Demonstrates the ckanapi resource dump functionality
"""

import json
import asyncio
from mcp_ckan_server import CKANAPIClient


async def example_dump_resource():
    """Example: Download and dump a single resource"""
    
    client = CKANAPIClient(
        base_url='https://demo.ckan.org',
        api_key=None
    )
    
    print("=== Dumping a Single Resource from CKAN ===\n")
    
    async with client as c:
        # Step 1: Find a dataset with resources
        print("1. Searching for datasets with CSV resources...")
        try:
            search_result = await client.call_action(
                "package_search",
                q='res_format:CSV',
                rows=1
            )
            
            if not search_result.get('results'):
                print("   No CSV resources found. Let's list some packages...")
                packages = await client.call_action("package_list", limit=3)
                print(f"   Available packages: {packages}")
                return
            
            package = search_result['results'][0]
            print(f"   ✓ Found package: {package['name']}")
            
            if not package.get('resources'):
                print("   Package has no resources")
                return
            
            resource = package['resources'][0]
            resource_id = resource['id']
            resource_name = resource.get('name', 'Unnamed resource')
            resource_url = resource.get('url', 'N/A')
            
            print(f"   ✓ Found resource: {resource_name}")
            print(f"   ✓ Resource ID: {resource_id}")
            print(f"   ✓ Resource URL: {resource_url}")
            
            # Step 2: Get resource details (using MCP tool approach)
            print(f"\n2. Fetching resource metadata...")
            resource_meta = await client.call_action("resource_show", id=resource_id)
            print(f"   ✓ Format: {resource_meta.get('format', 'Unknown')}")
            print(f"   ✓ Size: {resource_meta.get('size', 'Unknown')} bytes")
            print(f"   ✓ Last modified: {resource_meta.get('last_modified', 'Unknown')}")
            
            # Step 3: If the resource is a URL, show how to download it
            print(f"\n3. Resource download information:")
            if resource_meta.get('url'):
                print(f"   Direct download URL: {resource_meta['url']}")
                print(f"   Expected format: {resource_meta.get('format', 'Unknown')}")
            
            # Show the full resource metadata
            print(f"\n4. Full resource metadata (JSON):")
            print(json.dumps(resource_meta, indent=2))
            
        except Exception as e:
            print(f"   ✗ Error: {e}")


async def example_using_ckanapi_methods():
    """Example: Using ckanapi RemoteCKAN to dump resources directly"""
    
    print("\n\n=== Using ckanapi RemoteCKAN directly ===\n")
    
    client = CKANAPIClient(
        base_url='https://demo.ckan.org',
        api_key=None
    )
    
    async with client as c:
        # Access the underlying RemoteCKAN client
        print("1. Accessing RemoteCKAN client methods...")
        print(f"   Client type: {type(c.client)}")
        print(f"   Base URL: {c.client.base_url}")
        
        # Example: You can use the session to download resources directly
        print("\n2. Direct resource download using requests session:")
        try:
            # Get a package with resources
            package = await client.call_action("package_show", id="sample-organization")
            if package.get('resources'):
                resource = package['resources'][0]
                url = resource.get('url')
                
                if url and url.startswith('http'):
                    print(f"   Resource URL: {url}")
                    print(f"   Size: {resource.get('size', 'Unknown')} bytes")
                    
                    # You can download it directly using the session
                    print(f"\n   To download this resource programmatically:")
                    print(f"   ```python")
                    print(f"   response = client.client.session.get('{url}')")
                    print(f"   with open('downloaded_file', 'wb') as f:")
                    print(f"       f.write(response.content)")
                    print(f"   ```")
        except Exception as e:
            print(f"   Note: {e}")


async def main():
    """Run all examples"""
    await example_dump_resource()
    await example_using_ckanapi_methods()
    
    print("\n\n✅ Examples completed!")
    print("\nKey takeaways:")
    print("- Use 'ckan_resource_show' MCP tool to get resource metadata and download URL")
    print("- Use 'ckan_resource_download' MCP tool with output_format='json' to parse JSON resources")
    print("- RemoteCKAN session can be used directly for advanced downloads")


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
