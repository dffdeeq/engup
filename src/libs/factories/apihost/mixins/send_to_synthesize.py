from src.libs.factories.apihost.base import BaseApiHostClient
from src.libs.factories.apihost.models.synthesize_request import SynthesizeRequest, SynthesizeData
from src.libs.factories.apihost.models.synthesize_response import SynthesizeResponse
from src.libs.factories.apihost.routes import SEND_TEXT_TO_SYNTHESIZE


class SendTextToSynthesizeMixin(BaseApiHostClient):
    async def send_text_to_synthesize(self, text: str) -> SynthesizeResponse:
        data = SynthesizeData(text=text)
        payload = SynthesizeRequest(data=data)
        response = await self.request('POST', SEND_TEXT_TO_SYNTHESIZE, data=payload.model_dump())

        return SynthesizeResponse(**response.body)
