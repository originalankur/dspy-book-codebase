import asyncio
from fastmcp import Client # <1>

async def main():
    mcp_url = "http://127.0.0.1:8000/mcp" # <2>
    
    try:
        async with Client(mcp_url, auth="oauth") as client: # <3>
            tools = await client.list_tools() # <4>
            print(f"Discovered {len(tools)} tools: {[tool.name for tool in tools]}\n")
            
            for tool in tools:
                print(f"Calling {tool.name}...")
                try:
                    result = await client.call_tool(tool.name) # <5>
                    print(f"{result.content}\n")
                except Exception as e:
                    print(f"Error calling {tool.name}: {e}\n")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

