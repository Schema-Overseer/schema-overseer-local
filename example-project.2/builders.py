from typing import Literal

from pydantic import BaseModel, ValidationError

from .models import ApplicationContext, schema_registry
from .schema import ConfigV1, ConfigV2


@schema_registry.add
def builder(config: "ConfigV1") -> ApplicationContext:
    try:
        return ApplicationContext(my_var=int(config.my_old_var))
    except ValueError as error:
        raise ValidationError([[error]], ApplicationContext) from error


@schema_registry.add
def builder(config: ConfigV2) -> ApplicationContext:
    return ApplicationContext(my_var=int(config.my_new_var))
