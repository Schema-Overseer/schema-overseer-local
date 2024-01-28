from dataclasses import dataclass
from typing import Callable

from pydantic import BaseModel

from schema_overseer_local import SchemaRegistry


def my_function():
    print('This was an old input')


def my_other_function():
    print('This was a new input')


@dataclass
class Output:
    value: int
    function: Callable[[], None]


schema_registry = SchemaRegistry(Output)


@schema_registry.add_scheme
class OldInputFormat(BaseModel):
    value: str


@schema_registry.add_scheme
class NewInputFormat(BaseModel):
    renamed_value: int


@schema_registry.add_builder
def old_builder(data: OldInputFormat) -> Output:
    return Output(
        value=data.value,
        function=my_function,
    )


@schema_registry.add_builder
def new_builder(data: NewInputFormat) -> Output:
    return Output(
        value=data.renamed_value,
        function=my_other_function,
    )
