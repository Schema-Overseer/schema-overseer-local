from __future__ import annotations

import datetime
from typing import Any

from pydantic import AnyHttpUrl, BaseModel, model_validator

from ..registry import payload_schema_registry


@payload_schema_registry.add_schema
class NewPayload(BaseModel):
    text: str | None = None
    image: AnyHttpUrl | None = None
    created_at: datetime.datetime | None = None

    @model_validator(mode='before')
    @classmethod
    def check_source(cls, values: dict[str, Any]) -> dict[str, Any]:
        mutually_required_fields = ['text', 'image']
        if not any(field in values for field in mutually_required_fields):
            msg = f"At least one of the following fields must be present: {', '.join(mutually_required_fields)}"
            raise ValueError(msg)

        return values
