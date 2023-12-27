from typing import Literal

from pydantic import BaseModel, ValidationError

from .models import ApplicationContext


class BaseConfig(BaseModel):
    pass


class ConfigV1(BaseConfig):
    my_old_var: str
    version: Literal["v1"] | None = None


class ConfigV2(BaseConfig):
    my_new_var: float
    version: Literal["v2"] = "v2"


class UnexpectedScheme(Exception):
    pass


def to_context_v1(config: ConfigV1) -> ApplicationContext:
    try:
        return ApplicationContext(my_var=int(config.my_old_var))
    except ValueError as error:
        raise ValidationError([[error]], ApplicationContext) from error


def to_context_v2(config: ConfigV2) -> ApplicationContext:
    return ApplicationContext(my_var=int(config.my_new_var))


schema_classes: list[type[BaseConfig]] = {
    ConfigV1: to_context_v1,
    ConfigV2: to_context_v2,
}


def resolve_scheme(value: dict) -> ApplicationContext:
    for schema_class, resolver in schema_classes.items():
        try:
            parsed = schema_class.model_validate(value)
            return resolver(parsed)

        except ValidationError:
            continue
    else:
        raise UnexpectedScheme("No suitable scheme found for given input")
