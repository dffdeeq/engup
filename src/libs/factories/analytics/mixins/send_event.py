import logging

from src.libs.factories.analytics.base import BaseAnalyticsClient
from src.libs.factories.analytics.models.event_data import EventData


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
