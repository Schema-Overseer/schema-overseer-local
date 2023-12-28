import datetime

from pydantic import AnyHttpUrl, BaseModel

from ..registry import payload_schema_registry


@payload_schema_registry.add_scheme
class NewPayload(BaseModel):
    text: str | None = None
    image: AnyHttpUrl | None = None
    created_at: datetime.datetime | None = None
