import os
import typing as T # noqa
from pathlib import Path

import aiohttp

from src.libs.factories.apihost.base import BaseApiHostClient
from src.libs.factories.apihost.models.STTText import STTText
from src.libs.factories.apihost.routes import SPEECH_TO_TEXT_ROUTE


class SpeechToTextMixin(BaseApiHostClient):
    async def speech_to_text(
        self,
        filepath: str | Path,
    ) -> STTText:
        data = aiohttp.FormData()
        data.add_field('file', open(filepath, 'rb'), filename=os.path.basename(filepath))
        response = await self.request('POST', SPEECH_TO_TEXT_ROUTE, data=data)
        return STTText(**response.body)
