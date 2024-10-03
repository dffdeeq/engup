import pydantic


class MessageResponse(pydantic.BaseModel):
    message: str
