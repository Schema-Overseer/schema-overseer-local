import pytest
from pydantic import BaseModel

from schema_overseer_local import SchemaRegistry
from schema_overseer_local.exceptions import MultipleValidSchemasError


def test_check_for_single_valid_schema() -> None:
    """
    Test that SchemaRegistry raises MultipleValidSchemasError when check_for_single_valid_schema is True
    and there are multiple valid schemas
    """
    schema_registry = SchemaRegistry(int, check_for_single_valid_schema=True)

    @schema_registry.add_schema
    class InputFormat1(BaseModel):
        value: str

    @schema_registry.add_schema
    class InputFormat2(BaseModel):
        value: str

    @schema_registry.add_builder
    def builder_1(data: InputFormat1) -> int:
        return int(data.value)

    @schema_registry.add_builder
    def builder_2(data: InputFormat2) -> int:
        return int(data.value)

    schema_registry.setup()

    with pytest.raises(MultipleValidSchemasError):
        schema_registry.build(source_dict={'value': '123'})
