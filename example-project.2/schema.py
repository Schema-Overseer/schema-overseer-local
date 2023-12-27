from typing import Literal

from pydantic import BaseModel

from .models import schema_registry


@schema_registry.add
class ConfigV1(BaseModel):
    my_old_var: str
    version: Literal["v1"] | None = None


@schema_registry.add
class ConfigV2(BaseModel):
    my_new_var: float
    version: Literal["v2"] = "v2"
