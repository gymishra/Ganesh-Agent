import asyncio
import aiohttp
import json
from odata_model_training import ODataClassifier

class ODataSSEIntegration:
    def __init__(self, classifier: ODataClassifier):
        self.classifier = classifier
        
    async def listen_events(self, sse_url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(sse_url) as resp:
                async for line in resp.content:
                    if line.startswith(b'data: '):
                        event = json.loads(line[6:].decode())
                        await self.handle_event(event)
    
    async def handle_event(self, event: dict):
        print(f"OData Event: {event['type']} on {event['service']}")
        # Update classifier with real-time service status
        if event['type'] == 'data_change':
            self.classifier.update_service_status(event['service'], 'active')

# Usage with existing classifier
async def run_with_sse():
    classifier = ODataClassifier()
    sse_integration = ODataSSEIntegration(classifier)
    await sse_integration.listen_events("http://localhost:8080/events")

if __name__ == "__main__":
    asyncio.run(run_with_sse())
