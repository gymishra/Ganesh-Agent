import asyncio
import aiohttp
import json
from typing import AsyncGenerator

class ODataSSEClient:
    def __init__(self, sse_endpoint: str):
        self.sse_endpoint = sse_endpoint
        
    async def stream_events(self) -> AsyncGenerator[dict, None]:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.sse_endpoint) as resp:
                async for line in resp.content:
                    if line.startswith(b'data: '):
                        try:
                            data = json.loads(line[6:].decode())
                            yield data
                        except json.JSONDecodeError:
                            continue

# Integration with existing classifier
def integrate_sse_with_classifier():
    """Add SSE monitoring to existing OData classifier"""
    
    async def monitor_services():
        client = ODataSSEClient("http://localhost:8080/events")
        async for event in client.stream_events():
            print(f"OData Event: {event['type']} on {event['service']}")
            # Update classifier with real-time service status
            
    return monitor_services

if __name__ == "__main__":
    monitor = integrate_sse_with_classifier()
    asyncio.run(monitor())
