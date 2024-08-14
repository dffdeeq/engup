import asyncio
import logging
import uuid

from src.libs.factories.analytics.base import BaseAnalyticsClient
from src.libs.factories.analytics.models.event_data import EventData
from src.libs.http_client import HttpClient
from src.settings import Settings


class SendEventMixin(BaseAnalyticsClient):
    async def send_event(self, client_id: str, event_data: EventData):
        params = {
            "category": "payment",
            "action": "complete",
            "label": "telegram_bot",
            "value": 100,
            "source": event_data.utm_source,
            "medium": event_data.utm_medium,
            "campaign": event_data.utm_campaign,
            "content": event_data.utm_content
        }

        payload = {
            "client_id": client_id,
            "events": [
                {
                    "name": event_data.event_name,
                    "params": params
                }
            ]
        }
        response = await self.request('POST', '/collect', json=payload, params={'measurement_id': 'G-FJR3TBQ19F'})
        if response.status == 204 or response.status == 200:
            return
        else:
            logging.error('Failed sending event to Google Analytics')


async def main(client: SendEventMixin):
    client_id = str(uuid.uuid4())
    await client.send_event(client_id, EventData(
        utm_source='test1',
        utm_medium='test2',
        utm_campaign='test3',
        utm_content='test4',
        event_name='conversion_event_begin_checkout',
    ))


if __name__ == '__main__':
    settings = Settings.new()
    http_client = HttpClient()
    client = SendEventMixin(http_client, settings.analytics)
    asyncio.run(main(client))
