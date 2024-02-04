from pydantic import BaseModel

from ..registry import payload_schema_registry


@payload_schema_registry.add_schema
class OldPayload(BaseModel):
    query: str

    def to_message(self) -> str:
        return self.query
