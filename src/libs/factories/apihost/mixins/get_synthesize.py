import typing as T # noqa

from src.libs.factories.apihost.base import BaseApiHostClient
from src.libs.factories.apihost.models.synthesize_request import SynthesizeGetRequest
from src.libs.factories.apihost.routes import GET_SYNTHESIZE


class GetSynthesizeMixin(BaseApiHostClient):
    async def get_synthesize(self, process: str) -> T.Optional[str]:
        payload = SynthesizeGetRequest(process=process)
        response = await self.request('POST', GET_SYNTHESIZE, data=payload.model_dump())

        return response.body.get('message', None)
