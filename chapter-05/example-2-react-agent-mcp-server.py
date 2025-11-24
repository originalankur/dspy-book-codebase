import asyncio
import json
import sys
import dspy
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

class WebPageInvestigationSignature(dspy.Signature): # <1>
    """Investigate a webpage to find failed URLs and JavaScript errors."""
    task: str = dspy.InputField(desc="The investigation task to perform on the webpage")
    failed_urls: str = dspy.OutputField(desc="Return a JSON array of objects with failed_url, status_code, and reason as keys. Return raw text, not Markdown.")
    console_errors: str = dspy.OutputField(desc="Return a JSON array of objects with console_errors and fixes as keys. Return raw text, not Markdown.")

async def investigate_webpage(url: str, mcp_url: str = "http://localhost:8931/mcp"): # <2>
    async with streamablehttp_client(mcp_url) as (read, write, session):
        async with ClientSession(read, write) as client_session:
            await client_session.initialize()
            tools_response = await client_session.list_tools()
            dspy_tools = []
            for tool in tools_response.tools:
                dspy_tools.append(dspy.Tool.from_mcp_tool(client_session, tool)) # <2>
            react = dspy.ReAct(WebPageInvestigationSignature, tools=dspy_tools) # <3>
            task = f"Open {url}, wait for page to load. Check for any failed network requests (non-200 status) in browser network calls. Also check for any JavaScript console errors." # <4>
            
            result = await react.acall(task=task) # <5>
            
            await client_session.call_tool("browser_close", {}) # <6>            
            return result

async def main(url):
    dspy.configure(lm=dspy.LM('gemini/gemini-2.0-flash'))

    result = await investigate_webpage(url) # <7>
    print(result.failed_urls) # <8>
    print(result.console_errors) # <9>

    for key, value in sorted(result.trajectory.items()): # <10>
        if key.startswith('tool_name_'):
            print(f"{key}: {value}")


if __name__ == "__main__":
    url = sys.argv[1] if len(sys.argv) > 1 else "https://dspyweekly.com"
    asyncio.run(main(url))

