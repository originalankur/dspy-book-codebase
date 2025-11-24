import asyncio
import json

from mcp import ClientSession # <1>
from mcp.client.streamable_http import streamablehttp_client # <2>

async def connect_to_mcp_server(mcp_url: str = "http://localhost:8931/mcp"): # <4>
    async with streamablehttp_client(mcp_url) as (read, write, session):
        async with ClientSession(read, write) as client_session:
            await client_session.initialize() # <5>           
            tools_response = await client_session.list_tools() 
            for tool in tools_response.tools:
                print(f"  - {tool.name}: {tool.description}")

async def main() -> None:
    """Main entry point."""
    await connect_to_mcp_server()

if __name__ == "__main__":
    asyncio.run(main()) # <3>
