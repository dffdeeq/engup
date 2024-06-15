import os
import typing as T # noqa
from pathlib import Path

import aiohttp

from src.libs.factories.apihost.base import BaseApiHostClient
from src.libs.factories.apihost.models.transcription_response import TranscriptionResponse
from src.libs.factories.apihost.routes import SEND_FILES_TO_TRANSCRIPTION


class SendAudioToTranscriptionMixin(BaseApiHostClient):
    async def send_files_to_transcription(self, filepaths: T.List[str | Path],) -> TranscriptionResponse:
        data = aiohttp.FormData()
        for filepath in filepaths:
            with open(filepath, 'rb') as file:
                data.add_field('files', file, filename=os.path.basename(filepath))

        response = await self.request('POST', SEND_FILES_TO_TRANSCRIPTION, data=data)
        return TranscriptionResponse(**response.body)
