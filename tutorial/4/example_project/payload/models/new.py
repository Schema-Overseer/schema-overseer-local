import datetime

from pydantic import AnyHttpUrl, BaseModel, model_validator

from ..registry import payload_schema_registry


@payload_schema_registry.add_scheme
class NewPayload(BaseModel):
    text: str | None = None
    image: AnyHttpUrl | None = None
    created_at: datetime.datetime | None = None

    @model_validator(mode="before")
    def check_source(cls, values):
        MUTUALLY_REQUIRED_FIELDS = ["text", "image"]
        if not any(field in values for field in MUTUALLY_REQUIRED_FIELDS):
            raise ValueError(
                f"At least one of the following fields must be present: {', '.join(MUTUALLY_REQUIRED_FIELDS)}"
            )

        return values
