import aiohttp
from typing import Dict, Any, List


class WebhookHandler:
    async def register_webhook(
        self, webhook_url: str, events: List[str]
    ) -> Dict[str, Any]:
        async with aiohttp.ClientSession() as session:
            data = {"url": webhook_url, "events": events}
            async with session.post(f"{self.base_url}/webhooks", json=data) as response:
                response.raise_for_status()
                return await response.json()

    async def process_webhook(self, payload: Dict[str, Any]) -> None:
        event_type = payload.get("event_type")
        if event_type:
            # Process the webhook payload based on the event type
            pass
