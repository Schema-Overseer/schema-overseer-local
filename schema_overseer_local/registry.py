from __future__ import annotations

import inspect
from dataclasses import is_dataclass
from typing import Any, Callable, Generic, Sequence, TypeVar, cast, overload

from pydantic import BaseModel, TypeAdapter, ValidationError
from typing_extensions import get_type_hints

from .exceptions import MultipleValidSchemasError, NoMatchingSchemaError, OutputValidationError, SetupError
from .utils import import_string

_OutputType = TypeVar('_OutputType')
_InputSchema = TypeVar('_InputSchema', bound=BaseModel)


class SchemaRegistry(Generic[_OutputType]):
    validate_output: bool
    check_for_single_valid_schema: bool
    _output_type: type[_OutputType]
    _discovery_paths: Sequence[str]
    _storage: dict[type[BaseModel], Callable[[BaseModel], _OutputType] | None]
    _setup_done: bool

    def __init__(
        self,
        output_type: type[_OutputType],
        *,
        discovery_paths: Sequence[str] = (),
        validate_output: bool = False,
        check_for_single_valid_schema: bool = False,
    ) -> None:
        self._output_type = output_type
        self._discovery_paths = discovery_paths
        self._storage = {}
        self._setup_done = False
        self.validate_output = validate_output
        self.check_for_single_valid_schema = check_for_single_valid_schema

    def add_schema(self, model: type[_InputSchema]) -> type[_InputSchema]:
        self._storage[model] = None
        return model

    def add_builder(
        self, builder_func: Callable[[_InputSchema], _OutputType]
    ) -> Callable[[_InputSchema], _OutputType]:
        builder_type_hints = get_type_hints(builder_func)
        sign = inspect.signature(builder_func)

        if len(sign.parameters) < 1:
            msg = f'Builder "{builder_func.__name__}" doesn\'t have argument for the input data'
            raise SetupError(msg)

        parameter, *subsequent_params = sign.parameters.values()

        if not all(p.default is not inspect._empty for p in subsequent_params):
            msg = f'Builder "{builder_func.__name__}" has too many arguments without default values'
            raise SetupError(msg)

        if parameter.annotation is inspect._empty:
            msg = f'Argument type annotation is missing for builder "{builder_func.__name__}"'
            raise SetupError(msg)

        model = builder_type_hints[parameter.name]

        if model not in self._storage:
            msg = f'Attempt to register builder for the unregistered schema: {model!r}'
            raise SetupError(msg)

        if sign.return_annotation is inspect._empty:
            msg = f'Return type annotation is missing for builder "{builder_func.__name__}"'
            raise SetupError(msg)

        if builder_type_hints['return'] != self._output_type:
            msg = (
                f'Return type annotation of builder "{builder_func.__name__}" '
                f'must be "{self._output_type}" instead of "{sign.return_annotation}"'
            )
            raise SetupError(msg)

        builder_func = cast(Callable[[BaseModel], _OutputType], builder_func)

        self._storage[model] = builder_func
        return builder_func

    def setup(self) -> None:
        for path in self._discovery_paths:
            import_string(path)

        if any(builder is None for builder in self._storage.values()):
            schema_without_builders = ', '.join(s.__name__ for s, b in self._storage.items() if b is None)
            msg = f'Missing builders for the following schema: {schema_without_builders}'
            raise SetupError(msg)
        self._setup_done = True

    @overload
    def build(self, *, source_dict: dict[str, Any], source_object: None = None) -> _OutputType:
        """Build output object from dict-like object"""
        ...

    @overload
    def build(self, *, source_object: Any, source_dict: None = None) -> _OutputType:
        """Build output object from instance using attributes"""
        ...

    def build(
        self,
        *,
        source_dict: dict[str, Any] | None = None,
        source_object: Any | None = None,
    ) -> _OutputType:
        """
        Build output object from dict or instance using attributes.
        Raises:
            NoMatchingSchemaError: if no input schema was matched
            ValidateOutputError: if output validation failed
        """
        assert self._setup_done, 'setup() method must be called before building'
        assert (source_dict is None) ^ (source_object is None), 'Use either `source_dict` or `source_object` arguments'

        valid_input_objects: list[tuple[type[BaseModel], BaseModel]] = []

        for model in self._storage:
            try:
                if source_dict is not None:
                    obj = model(**source_dict)
                elif source_object is not None:
                    obj = model.model_validate(source_object, from_attributes=True)
                else:
                    assert False
            except ValidationError:
                continue

            valid_input_objects.append((model, obj))
            if not self.check_for_single_valid_schema:
                break  # we already have one suitable input object

        if not valid_input_objects:
            raise NoMatchingSchemaError()

        elif len(valid_input_objects) > 1 and self.check_for_single_valid_schema:
            raise MultipleValidSchemasError()

        else:
            model, obj = valid_input_objects[0]
            builder = self._storage[model]
            assert builder is not None

            output = builder(obj)

            if self.validate_output:
                try:
                    return self.perform_validate_output(output)
                except ValidationError as error:
                    raise OutputValidationError from error
            else:
                return output

    def perform_validate_output(self, output: _OutputType) -> _OutputType:
        """Override this method to provide custom output validation."""

        # https://github.com/pydantic/pydantic-core/issues/755
        data: Any
        if is_dataclass(self._output_type):
            data = output.__dict__
        elif isinstance(output, BaseModel):
            data = output.model_dump(mode='python')
        else:
            data = output
        return TypeAdapter(self._output_type).validate_python(data)
