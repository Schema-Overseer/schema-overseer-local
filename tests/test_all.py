from typing import Any, Dict
from pydantic import BaseModel
from dataclasses import dataclass

import pytest
from schema_overseer_local import SchemaRegistry


@pytest.mark.parametrize(
    'raw_data',
    [
        {'value': '123'},
        {'renamed_value': 123},
    ],
)  # type: ignore[misc]
def test_default_use_case(raw_data: Dict[str, Any]) -> None:
    @dataclass
    class TestContext:
        value: str

    schema_registry = SchemaRegistry(TestContext)

    @schema_registry.add_scheme
    class OldInputFormat(BaseModel):
        value: str

    @schema_registry.add_scheme
    class NewInputFormat(BaseModel):
        renamed_value: int

    @schema_registry.add_builder
    def old_builder(data: OldInputFormat) -> TestContext:
        return TestContext(value=data.value)

    @schema_registry.add_builder
    def new_builder(data: NewInputFormat) -> TestContext:
        return TestContext(value=str(data.renamed_value))

    schema_registry.setup()

    context = schema_registry.build(source_dict=raw_data)

    assert context.value == '123'
