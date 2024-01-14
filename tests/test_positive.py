from dataclasses import dataclass
from typing import Any, Dict, Union

import pytest
from pydantic import BaseModel

from schema_overseer_local import SchemaRegistry


@dataclass
class Output:
    value: str


schema_registry = SchemaRegistry(Output)


@schema_registry.add_scheme
class OldInputFormat(BaseModel):
    value: str


@schema_registry.add_scheme
class NewInputFormat(BaseModel):
    renamed_value: int


@schema_registry.add_builder
def old_builder(data: OldInputFormat) -> Output:
    return Output(value=data.value)


@schema_registry.add_builder
def new_builder(data: NewInputFormat) -> Output:
    return Output(value=str(data.renamed_value))


schema_registry.setup()


@pytest.mark.parametrize(
    'raw_data',
    [
        {'value': '123'},
        {'renamed_value': 123},
    ],
)
def test_dict_source(raw_data: Dict[str, Any]) -> None:
    output = schema_registry.build(source_dict=raw_data)

    assert output.value == '123'


@dataclass
class OldInput:
    value: str


@dataclass
class NewInput:
    renamed_value: int


@pytest.mark.parametrize(
    'raw_data',
    [
        OldInput(value='123'),
        NewInput(renamed_value=123),
    ],
)
def test_object_source(raw_data: Union[OldInput, NewInput]) -> None:
    output = schema_registry.build(source_object=raw_data)

    assert output.value == '123'
