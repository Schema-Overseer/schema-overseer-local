from dataclasses import dataclass
from typing import Any

import pytest
from pydantic import BaseModel

from schema_overseer_local import SchemaOverseerSetupError, SchemaRegistry


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


def test_missing_builder() -> None:
    @schema_registry.add_builder
    def old_builder(data: OldInputFormat) -> Output:
        return Output(value=data.value)

    with pytest.raises(SchemaOverseerSetupError, match='NewInputFormat'):
        schema_registry.setup()


def test_extra_builder() -> None:
    class UnregisteredInputFormat(BaseModel):
        renamed_value: int

    with pytest.raises(SchemaOverseerSetupError, match='UnregisteredInputFormat'):

        @schema_registry.add_builder
        def builder(data: UnregisteredInputFormat) -> Output:
            return Output(value='test')


def test_builder_with_no_arg_annotation() -> None:
    with pytest.raises(SchemaOverseerSetupError, match='builder_with_no_arg_annotation'):

        @schema_registry.add_builder
        def builder_with_no_arg_annotation(data) -> Output:  # type: ignore[no-untyped-def]
            return Output(value='test')


def test_builder_with_no_return_annotation() -> None:
    with pytest.raises(SchemaOverseerSetupError, match='builder_with_no_return_annotation'):

        @schema_registry.add_builder
        def builder_with_no_return_annotation(data: OldInputFormat):  # type: ignore[no-untyped-def]
            return Output(value=data.value)


def test_builder_with_invalid_return_annotation() -> None:
    with pytest.raises(SchemaOverseerSetupError, match='builder_with_invalid_return_annotation'):

        @schema_registry.add_builder  # type: ignore[arg-type]
        def builder_with_invalid_return_annotation(data: OldInputFormat) -> str:
            return data.value


def test_builder_invalid_signature() -> None:
    with pytest.raises(SchemaOverseerSetupError, match='builder_with_invalid_signature'):

        @schema_registry.add_builder  # type: ignore[arg-type]
        def builder_with_invalid_signature() -> Output:
            return Output(value='test')


def test_builder_invalid_signature_too_many_args() -> None:
    with pytest.raises(SchemaOverseerSetupError, match='builder_with_invalid_signature'):

        @schema_registry.add_builder  # type: ignore[arg-type]
        def builder_with_invalid_signature(data: OldInputFormat, extra: Any) -> Output:
            return Output(value='test')


def test_extra_arguments_in_builder_is_fine_with_defaults() -> None:
    @schema_registry.add_builder
    def builder_with_extra_args(data: OldInputFormat, extra: str = 'test') -> Output:
        return Output(value='test')
