from pydantic import AnyHttpUrl, BaseModel, ValidationError


class BasePayload(BaseModel):
    def to_message(self) -> str:
        raise NotImplementedError


class OldPayload(BasePayload):
    query: str

    def to_message(self) -> str:
        return self.query


class NewPayload(BasePayload):
    text: str | None = None
    image: AnyHttpUrl | None = None

    def to_message(self) -> str:
        text_log_entry = "<no text>" if self.text is None else self.text
        image_log_entry = "empty" if self.image is None else self.image
        return f'{text_log_entry} | <image "{image_log_entry}">'


class InvalidPayload(Exception):
    pass


payload_models: list[type[BasePayload]] = [
    OldPayload,
    NewPayload,
]


def build_log_entry(value: dict) -> str:
    for model in payload_models:
        try:
            payload = model.model_validate(value)
            return payload.to_message()

        except ValidationError:
            continue
    else:
        raise InvalidPayload("No suitable payload scheme found for given input")
