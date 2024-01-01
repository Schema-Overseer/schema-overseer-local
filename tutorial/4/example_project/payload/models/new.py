import datetime
from typing import Any, Dict, Optional

from pydantic import AnyHttpUrl, BaseModel, model_validator

from ..registry import payload_schema_registry


@payload_schema_registry.add_scheme
class NewPayload(BaseModel):
    text: Optional[str] = None
    image: Optional[AnyHttpUrl] = None
    created_at: Optional[datetime.datetime] = None

    @model_validator(mode='before')
    @classmethod
    def check_source(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        mutually_required_fields = ['text', 'image']
        if not any(field in values for field in mutually_required_fields):
            msg = f"At least one of the following fields must be present: {', '.join(mutually_required_fields)}"
            raise ValueError(msg)

        return values
