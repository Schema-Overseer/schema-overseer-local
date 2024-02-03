from dataclasses import dataclass
from typing import Callable

from pydantic import BaseModel, ValidationError

from schema_overseer_local import SchemaRegistry


def my_function() -> None:
    print('This was an old input')


def my_other_function() -> None:
    print('This was a new input')


@dataclass
class Output:
    value: int
    function: Callable[[], None]


schema_registry = SchemaRegistry(Output)


@schema_registry.add_schema
class OldInputFormat(BaseModel):
    value: str


@schema_registry.add_schema
class NewInputFormat(BaseModel):
    renamed_value: int


@schema_registry.add_builder
def old_builder(data: OldInputFormat) -> Output:
    try:
        return Output(
            value=int(data.value),
            function=my_function,
        )
    except ValueError as error:
        raise ValidationError() from error


@schema_registry.add_builder
def new_builder(data: NewInputFormat) -> Output:
    return Output(
        value=data.renamed_value,
        function=my_other_function,
    )
