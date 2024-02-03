from dataclasses import dataclass

import pytest
from pydantic import BaseModel
from typing_extensions import reveal_type

from schema_overseer_local.registry import SchemaRegistry


@pytest.mark.mypy_testing()
def test_output_type() -> None:
    @dataclass
    class Output:
        value: str

    schema_registry = SchemaRegistry(Output)
    reveal_type(
        schema_registry  # N: Revealed type is "schema_overseer_local.registry.SchemaRegistry[tests.test_mypy.Output@13]"
    )

    @schema_registry.add_schema
    class InputFormat(BaseModel):
        value: str

    @schema_registry.add_builder
    def builder(data: InputFormat) -> Output:
        return Output(value=data.value)

    schema_registry.setup()
    output = schema_registry.build(source_dict={'value': '123'})
    reveal_type(output)  # N: Revealed type is "tests.test_mypy.Output@13"
