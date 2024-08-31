import logging

from src.libs.factories.apihost.base import BaseApiHostClient
from src.libs.factories.apihost.models.synthesize_request import SynthesizeRequest, SynthesizeData
from src.libs.factories.apihost.models.synthesize_response import SynthesizeResponse
from src.libs.factories.apihost.routes import SEND_TEXT_TO_SYNTHESIZE


class SendTextToSynthesizeMixin(BaseApiHostClient):
    async def send_text_to_synthesize(self, text: str) -> SynthesizeResponse:
        data = SynthesizeData(text=text)
        payload = SynthesizeRequest(data=data)
        payload_dump = payload.model_dump()
        logging.info(payload_dump)
        response = await self.request('POST', SEND_TEXT_TO_SYNTHESIZE, json=payload_dump)
        logging.info(response)

        return SynthesizeResponse(**response.body)
