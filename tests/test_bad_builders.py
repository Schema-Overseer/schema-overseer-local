from dataclasses import dataclass
from typing import Any

import pytest
from pydantic import BaseModel

from schema_overseer_local import SchemaRegistry, SetupError


@dataclass
class Output:
    value: str


schema_registry = SchemaRegistry(Output)


@schema_registry.add_schema
class OldInputFormat(BaseModel):
    value: str


@schema_registry.add_schema
class NewInputFormat(BaseModel):
    renamed_value: int


def test_missing_builder() -> None:
    """Tests that SetupError is raised when builder is missing for a registered schema"""

    @schema_registry.add_builder
    def old_builder(data: OldInputFormat) -> Output:
        return Output(value=data.value)

    with pytest.raises(SetupError, match='NewInputFormat'):
        schema_registry.setup()


def test_extra_builder() -> None:
    """Tests that SetupError is raised at attempt to register builder for unregistered schema"""

    class UnregisteredInputFormat(BaseModel):
        renamed_value: int

    with pytest.raises(SetupError, match='UnregisteredInputFormat'):

        @schema_registry.add_builder
        def builder(data: UnregisteredInputFormat) -> Output:
            return Output(value='test')


def test_builder_with_no_arg_annotation() -> None:
    """Tests that SetupError is raised when builder has no argument type annotation"""

    with pytest.raises(SetupError, match='builder_with_no_arg_annotation'):

        @schema_registry.add_builder
        def builder_with_no_arg_annotation(data) -> Output:  # type: ignore[no-untyped-def]
            return Output(value='test')


def test_builder_with_no_return_annotation() -> None:
    """Tests that SetupError is raised when builder has no return type annotation"""

    with pytest.raises(SetupError, match='builder_with_no_return_annotation'):

        @schema_registry.add_builder
        def builder_with_no_return_annotation(data: OldInputFormat):  # type: ignore[no-untyped-def]
            return Output(value=data.value)


def test_builder_with_invalid_return_annotation() -> None:
    """Tests that SetupError is raised when builder has invalid return type annotation"""

    with pytest.raises(SetupError, match='builder_with_invalid_return_annotation'):

        @schema_registry.add_builder  # type: ignore[arg-type]
        def builder_with_invalid_return_annotation(data: OldInputFormat) -> str:
            return data.value


def test_builder_invalid_signature_no_arguments() -> None:
    """Tests that SetupError is raised when builder has no arguments"""

    with pytest.raises(SetupError, match='builder_with_invalid_signature'):

        @schema_registry.add_builder  # type: ignore[arg-type]
        def builder_with_invalid_signature() -> Output:
            return Output(value='test')


def test_builder_invalid_signature_too_many_args() -> None:
    """Tests that SetupError is raised when builder has too many arguments"""

    with pytest.raises(SetupError, match='builder_with_invalid_signature'):

        @schema_registry.add_builder  # type: ignore[arg-type]
        def builder_with_invalid_signature(data: OldInputFormat, extra: Any) -> Output:
            return Output(value='test')


def test_extra_arguments_in_builder_is_fine_with_defaults() -> None:
    """Tests that builder with extra arguments with default values is registered successfully"""

    @schema_registry.add_builder
    def builder_with_extra_args(data: OldInputFormat, extra: str = 'test') -> Output:
        return Output(value='test')
