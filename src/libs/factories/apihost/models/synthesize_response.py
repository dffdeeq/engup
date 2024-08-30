from pydantic import BaseModel


class SynthesizeResponse(BaseModel):
    status: int
    process: str
    hold: float
