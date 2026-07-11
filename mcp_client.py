import os
import sys
import asyncio
import certifi
from pathlib import Path
from dotenv import load_dotenv
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_groq import ChatGroq


os.environ["SSL_CERT_FILE"] = certifi.where()
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")
AVIATION_STACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=GROQ_API_KEY
)

client = MultiServerMCPClient(
    {
        "tavily": {
            "transport": "streamable_http",
            "url": f"https://mcp.tavily.com/mcp/?tavilyApiKey={TAVILY_API_KEY}"
        },

        "Aviationstack MCP": {
            "transport": "stdio",
            "command": "uvx",
            "args": [
                "aviationstack-mcp"
            ],
            "env": {
                "AVIATION_STACK_API_KEY": AVIATION_STACK_API_KEY
            }
        },

        # FIX: this used to point at a *directory*, so the subprocess
        # never started. Point it at the actual server script, and run it
        # with the SAME interpreter that's running this app (sys.executable)
        # instead of a hardcoded, machine-specific path — that hardcoded
        # path also would have broken the moment you deployed to Render.
        "weather": {
            "transport": "stdio",
            "command": sys.executable,
            "args": [
                str(BASE_DIR / "custom_weather_mcp_server.py")
            ],
            "env": {
                "OPENWEATHER_API_KEY": OPENWEATHER_API_KEY
            }
        }
    }
)


# ---------------------------------------------------------------------------
# Shared tool cache.
#
# client.get_tools() opens a fresh connection to EVERY configured MCP
# server (tavily, aviation, weather) each time it's called. Calling it once
# per tool lookup — like the old code did — means every hotel/flight/
# weather request reconnects to all three servers. That's slow, and if any
# ONE server is briefly unreachable, the whole batch fails as a TaskGroup
# (that's what produced the "Connection closed" errors). Fetch once, cache,
# reuse for the lifetime of the process.
# ---------------------------------------------------------------------------
_tools_cache: list | None = None
_tools_lock = asyncio.Lock()


async def get_cached_tools():
    global _tools_cache

    if _tools_cache is not None:
        return _tools_cache

    async with _tools_lock:
        if _tools_cache is None:
            tools = await client.get_tools()
            print("\nAvailable MCP Tools:\n")
            for tool in tools:
                print(" -", tool.name)
            _tools_cache = tools

    return _tools_cache


def _find_tool(tools, name):
    for tool in tools:
        if tool.name == name:
            return tool
    raise ValueError(
        f"MCP tool '{name}' not found. Available tools: {[t.name for t in tools]}"
    )


async def tavily_mcp_search(query: str):
    tools = await get_cached_tools()
    search_tool = _find_tool(tools, "tavily_search")
    return await search_tool.ainvoke({"query": query})


async def aviation_mcp_call(tool_name: str, tool_args: dict = None):
    tools = await get_cached_tools()
    tool = _find_tool(tools, tool_name)
    return await tool.ainvoke(tool_args or {})


async def weather_mcp_search(city: str):
    tools = await get_cached_tools()
    weather_tool = _find_tool(tools, "get_current_weather")
    return await weather_tool.ainvoke({"city": city})


async def forecast_mcp_search(city: str):
    tools = await get_cached_tools()
    forecast_tool = _find_tool(tools, "get_forecast")
    return await forecast_tool.ainvoke({"city": city})


###################################
# Destination Extractor
###################################

def extract_destination(query: str):
    prompt = f"""
    Extract only the destination city or country.

    Query:
    {query}

    Return only destination name.
    """

    response = llm.invoke(prompt)
    return response.content.strip()