from pydantic import BaseModel


class SynthesizeData(BaseModel):
    lang: str = 'en-GB'
    speaker: str = '5218'
    emotion: str = 'neutral'
    text: str
    rate: str = '1.0'
    pitch: str = '1.0'
    type: str = 'mp3'
    pause: str = '0'


class SynthesizeRequest(BaseModel):
    data: SynthesizeData


class SynthesizeGetRequest(BaseModel):
    process: str
