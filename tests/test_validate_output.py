from __future__ import annotations

from dataclasses import dataclass

import pytest
from pydantic import BaseModel

from schema_overseer_local import OutputValidationError, SchemaRegistry


class InputFormat(BaseModel):
    value: str


@dataclass
class OutputDataclass:
    value: int


class OutputModel(BaseModel):
    value: int


def test_validate_output_dataclass() -> None:
    """Tests that output is validated when validate_output is True"""

    schema_registry = SchemaRegistry(OutputDataclass, validate_output=True)
    schema_registry.add_schema(InputFormat)

    @schema_registry.add_builder
    def builder(data: InputFormat) -> OutputDataclass:
        return OutputDataclass(value=int(data.value))

    schema_registry.setup()
    output = schema_registry.build(source_dict={'value': '123'})

    assert output.value == 123


def test_validate_output_dataclass_error() -> None:
    """Tests that OutputValidationError is raised when output is invalid"""

    schema_registry = SchemaRegistry(OutputDataclass, validate_output=True)
    schema_registry.add_schema(InputFormat)

    @schema_registry.add_builder
    def builder(data: InputFormat) -> OutputDataclass:
        return OutputDataclass(value='qwe')  # type: ignore[arg-type]

    schema_registry.setup()
    with pytest.raises(OutputValidationError):
        schema_registry.build(source_dict={'value': 'qwe'})


def test_validate_output_different_dataclass() -> None:
    """Tests that output is validated even for different dataclass"""

    @dataclass
    class OutputStrDataclass:
        value: str

    schema_registry = SchemaRegistry(OutputDataclass, validate_output=True)
    schema_registry.add_schema(InputFormat)

    @schema_registry.add_builder
    def builder(data: InputFormat) -> OutputDataclass:
        return OutputStrDataclass(value=data.value)  # type: ignore[return-value]

    schema_registry.setup()
    output = schema_registry.build(source_dict={'value': '123'})

    assert output.value == 123
    assert isinstance(output, OutputDataclass)


def test_validate_output_pydantic() -> None:
    """Tests that output is validated for pydantic models"""

    schema_registry = SchemaRegistry(OutputModel, validate_output=True)
    schema_registry.add_schema(InputFormat)

    @schema_registry.add_builder
    def builder(data: InputFormat) -> OutputModel:
        return OutputModel(value=int(data.value))

    schema_registry.setup()
    output = schema_registry.build(source_dict={'value': '123'})

    assert output.value == 123


def test_validate_output_pydantic_invalid() -> None:
    """Tests that OutputValidationError is raised when output is invalid for pydantic models"""

    schema_registry = SchemaRegistry(OutputModel, validate_output=True)
    schema_registry.add_schema(InputFormat)

    @schema_registry.add_builder
    def builder(data: InputFormat) -> OutputModel:
        return OutputModel.model_construct(value='qwe')  # type: ignore[arg-type]

    schema_registry.setup()
    with pytest.raises(OutputValidationError), pytest.warns(UserWarning):
        schema_registry.build(source_dict={'value': '123'})


def test_validate_output_pydantic_converts() -> None:
    """Tests that output is converted for pydantic models if validate_output is True"""

    schema_registry = SchemaRegistry(OutputModel, validate_output=True)
    schema_registry.add_schema(InputFormat)

    @schema_registry.add_builder
    def builder(data: InputFormat) -> OutputModel:
        return {'value': data.value}  # type: ignore[return-value]

    schema_registry.setup()
    output = schema_registry.build(source_dict={'value': '123'})

    assert output.value == 123
    assert isinstance(output, OutputModel)


def test_validate_output_int() -> None:
    """Tests that output is validated for int"""

    schema_registry = SchemaRegistry(int, validate_output=True)
    schema_registry.add_schema(InputFormat)

    @schema_registry.add_builder
    def builder(data: InputFormat) -> int:
        return data.value  # type: ignore[return-value]

    schema_registry.setup()
    output = schema_registry.build(source_dict={'value': '123'})

    assert output == 123
