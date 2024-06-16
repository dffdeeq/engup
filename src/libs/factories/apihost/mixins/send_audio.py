import os
import typing as T # noqa
from pathlib import Path

import aiofiles
import aiohttp

from src.libs.factories.apihost.base import BaseApiHostClient
from src.libs.factories.apihost.models.transcription_response import UploadResponse
from src.libs.factories.apihost.routes import SEND_FILES_TO_TRANSCRIPTION


class SendAudioToTranscriptionMixin(BaseApiHostClient):
    async def send_files_to_transcription(self, filepaths: T.List[str | Path],) -> UploadResponse:
        data = aiohttp.FormData()
        for filepath in filepaths:
            async with aiofiles.open(filepath, 'rb') as file:
                content = await file.read()
                data.add_field('files', content, filename=os.path.basename(filepath))

            response = await self.request('POST', SEND_FILES_TO_TRANSCRIPTION, data=data)
            return UploadResponse(**response.body)
