import asyncio
from fastmcp import Client, FastMCP
# HTTP server
client = Client("http://0.0.0.0:3210/mcp")

async def main():
    async with client:
        # Basic server interaction
        await client.ping()
        
        # List available operations
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()
        
        print(tools)
        
        # # Execute operations
        # result = await client.call_tool("example_tool", {"param": "value"})
        # print(result)

asyncio.run(main())