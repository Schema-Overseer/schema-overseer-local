from __future__ import annotations

from types import FunctionType
from typing import cast

from pydantic import BaseModel

from schema_overseer_local import SchemaRegistry


class InputFormat(BaseModel):
    value: str


def test_output_function() -> None:
    """Tests the possibility to use function as an output type"""

    schema_registry = SchemaRegistry(FunctionType)
    schema_registry.add_schema(InputFormat)

    @schema_registry.add_builder
    def builder(data: InputFormat) -> FunctionType:
        return cast(FunctionType, lambda: int(data.value))

    schema_registry.setup()
    output = schema_registry.build(source_dict={'value': '123'})

    assert output() == 123
