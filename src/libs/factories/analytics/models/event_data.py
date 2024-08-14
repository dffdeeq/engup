from pydantic import BaseModel


class EventData(BaseModel):
    utm_source: str
    utm_medium: str
    utm_campaign: str
    utm_content: str
    event_name: str
