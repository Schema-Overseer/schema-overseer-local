from typing import Literal
from pydantic import BaseModel, ValidationError
from .models import ApplicationContext


class BaseConfig(BaseModel):
    def to_context(self) -> ApplicationContext:
        ...


class ConfigV1(BaseConfig):
    my_old_var: str
    version: Literal['v1'] | None = None

    def to_context(self) -> ApplicationContext:
        try:
            return ApplicationContext(my_var=int(self.my_old_var))
        except ValueError as error:
            raise ValidationError([[error]], ApplicationContext) from error


class ConfigV2(BaseConfig):
    my_new_var: float
    version: Literal['v2'] = 'v2'

    def to_context(self) -> ApplicationContext:
        return ApplicationContext(my_var=int(self.my_new_var))


class UnexpectedScheme(Exception):
    pass


schema_classes: list[type[BaseConfig]] = {
    ConfigV1,
    ConfigV2,
}


def resolve_scheme(value: dict) -> ApplicationContext:
    for schema_class in schema_classes:
        try:
            parsed = schema_class.model_validate(value)
            return parsed.to_context()

        except ValidationError:
            continue
    else:
        raise UnexpectedScheme("No suitable scheme found for given input")
