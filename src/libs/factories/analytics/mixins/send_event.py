import typing as T  # noqa
import logging

from src.libs.factories.analytics.base import BaseAnalyticsClient


class SendEventMixin(BaseAnalyticsClient):
    async def send_event(self, client_id: str, event_name: str, umt_data_dict: T.Dict):
        umt_data_dict = umt_data_dict if umt_data_dict is not None else {}
        params = {
            "category": "payment",
            "action": "complete",
            "label": "telegram_bot",
            "value": 100,
            **umt_data_dict
        }
        logging.debug(f'params: {params}')

        payload = {
            "client_id": client_id,
            "events": [
                {
                    "name": event_name,
                    "params": params
                }
            ]
        }
        logging.debug(f'payload: {payload}')
        response = await self.request('POST', '/collect', json=payload, params={'measurement_id': 'G-FJR3TBQ19F'})
        logging.debug(response)
        if response.status == 204 or response.status == 200:
            return
        else:
            logging.error('Failed sending event to Google Analytics')
