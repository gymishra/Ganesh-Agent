#!/usr/bin/env python3
import asyncio
import json
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types
from aiohttp import web
import aiohttp_sse

app = Server("odata-sse-server")

@app.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="stream_odata_events",
            description="Stream real-time OData service events",
            inputSchema={
                "type": "object",
                "properties": {
                    "service": {"type": "string", "description": "OData service name"},
                    "events": {"type": "array", "items": {"type": "string"}}
                },
                "required": ["service"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    if name == "stream_odata_events":
        service = arguments["service"]
        
        # Start SSE endpoint
        sse_app = web.Application()
        
        async def events(request):
            async with aiohttp_sse.sse_response(request) as resp:
                for i in range(5):
                    event = {
                        "service": service,
                        "type": "data_change",
                        "entity": f"Customer{i+1}",
                        "timestamp": f"2024-01-{i+1:02d}T10:00:00Z"
                    }
                    await resp.send(json.dumps(event))
                    await asyncio.sleep(2)
            return resp
        
        sse_app.router.add_get('/events', events)
        runner = web.AppRunner(sse_app)
        await runner.setup()
        site = web.TCPSite(runner, 'localhost', 8080)
        await site.start()
        
        return [types.TextContent(
            type="text",
            text=f"SSE server started for {service} at http://localhost:8080/events"
        )]

async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, InitializationOptions())

if __name__ == "__main__":
    asyncio.run(main())
