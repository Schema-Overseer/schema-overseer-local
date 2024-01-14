import inspect
from typing import Any, Callable, Dict, Generic, Optional, Sequence, Type, TypeVar, cast, overload

from pydantic import BaseModel, ValidationError

from .utils import import_string


class InvalidSchemeError(Exception):
    """Could be raised in runtime during SchemaRegistry.build()"""


class SchemaOverseerSetupError(Exception):
    """Could be raised at registration of schema or builders or during SchemaRegistry.setup()"""


_OutputType = TypeVar('_OutputType')
_InputScheme = TypeVar('_InputScheme', bound=BaseModel)


class SchemaRegistry(Generic[_OutputType]):
    _output_type: Type[_OutputType]
    _discovery_paths: Sequence[str]
    _storage: Dict[Type[BaseModel], Optional[Callable[[BaseModel], _OutputType]]]
    _setup_done: bool

    def __init__(self, output_type: Type[_OutputType], discovery_paths: Sequence[str] = ()) -> None:
        self._output_type = output_type
        self._discovery_paths = discovery_paths
        self._storage = {}
        self._setup_done = False

    def add_scheme(self, model: Type[_InputScheme]) -> Type[_InputScheme]:
        self._storage[model] = None
        return model

    def add_builder(
        self, builder_func: Callable[[_InputScheme], _OutputType]
    ) -> Callable[[_InputScheme], _OutputType]:
        sign = inspect.signature(builder_func)

        if len(sign.parameters) < 1:
            msg = f'Builder "{builder_func.__name__}" doesn\'t have argument for the input data'
            raise SchemaOverseerSetupError(msg)

        parameter, *subsequent_params = sign.parameters.values()

        if not all(p.default is not inspect._empty for p in subsequent_params):
            msg = f'Builder "{builder_func.__name__}" has too many arguments without default values'
            raise SchemaOverseerSetupError(msg)

        model = parameter.annotation

        if model is inspect._empty:
            msg = f'Argument type annotation is missing for builder "{builder_func.__name__}"'
            raise SchemaOverseerSetupError(msg)

        if model not in self._storage:
            msg = f'Attempt to register builder for the unregistered scheme: {model.__name__}'
            raise SchemaOverseerSetupError(msg)

        if sign.return_annotation is inspect._empty:
            msg = f'Return type annotation is missing for builder "{builder_func.__name__}"'
            raise SchemaOverseerSetupError(msg)

        if sign.return_annotation != self._output_type:
            msg = (
                f'Return type annotation of builder "{builder_func.__name__}" '
                f'must be "{self._output_type}" instead of "{sign.return_annotation}"'
            )
            raise SchemaOverseerSetupError(msg)

        builder_func = cast(Callable[[BaseModel], _OutputType], builder_func)

        self._storage[model] = builder_func
        return builder_func

    def setup(self) -> None:
        for path in self._discovery_paths:
            import_string(path)

        if any(builder is None for builder in self._storage.values()):
            schema_without_builders = ', '.join(s.__name__ for s, b in self._storage.items() if b is None)
            msg = f'Missing builders for the following schema: {schema_without_builders}'
            raise SchemaOverseerSetupError(msg)
        self._setup_done = True

    @overload
    def build(self, *, source_dict: Dict[str, Any], source_object: None = None) -> _OutputType:
        """Build output object from dict"""
        ...

    @overload
    def build(self, *, source_object: Any, source_dict: None = None) -> _OutputType:
        """Build output object from instance using attributes"""
        ...

    def build(
        self,
        *,
        source_dict: Optional[Dict[str, Any]] = None,
        source_object: Optional[Any] = None,
    ) -> _OutputType:
        assert self._setup_done, 'setup() method must be called before building'
        assert (source_dict is None) ^ (source_object is None), 'Use either `source_dict` or `source_object` arguments'

        for model, builder in self._storage.items():
            assert builder is not None
            try:
                if source_dict is not None:
                    obj = model(**source_dict)
                elif source_object is not None:
                    obj = model.model_validate(source_object, from_attributes=True)
                else:
                    assert False

                return builder(obj)
            except ValidationError:
                pass
        raise InvalidSchemeError()
