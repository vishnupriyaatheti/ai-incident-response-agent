import asyncio
import sys

from mcp import Client, StdioServerParameters


SERVER = StdioServerParameters(
    command=sys.executable,
    args=["mcp/server.py"]
)


async def call_mcp_tool(tool_name, arguments):
    async with Client(SERVER) as client:
        result = await client.call_tool(
            tool_name,
            arguments
        )

        if result.is_error:
            raise RuntimeError(
                f"MCP tool failed: {tool_name}"
            )

        if result.structured_content is not None:
            return result.structured_content

        if result.content:
            first = result.content[0]

            if hasattr(first, "text"):
                import json
                return json.loads(first.text)

        return None


def call_mcp_tool_sync(tool_name, arguments):
    return asyncio.run(
        call_mcp_tool(tool_name, arguments)
    )