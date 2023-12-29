from inspect import signature
from typing import Any, Callable, Generic, TypeVar, cast

from pydantic import BaseModel, ValidationError

from .utils import import_string


class InvalidScheme(Exception):
    pass


Ctx = TypeVar("Ctx")
SchemeModel = TypeVar("SchemeModel", bound=BaseModel)


class SchemaRegistry(Generic[Ctx]):
    _context_type: type[Ctx]
    _discovery_paths: list[str]
    _storage: dict[type[BaseModel], Callable[[BaseModel], Ctx] | None]
    _setup_done: bool

    def __init__(self, context_type: type[Ctx], discovery_paths: list[str]) -> None:
        self._context_type = context_type
        self._discovery_paths = discovery_paths
        self._storage = {}
        self._setup_done = False

    def add_scheme(self, model: type[SchemeModel]) -> type[SchemeModel]:
        self._storage[model] = None
        return model

    def add_builder(
        self, builder_func: Callable[[SchemeModel], Ctx]
    ) -> Callable[[SchemeModel], Ctx]:
        sign = signature(builder_func)
        assert len(sign.parameters) == 1
        parameter = next(iter(sign.parameters.values()))
        model = parameter.annotation

        assert model in self._storage
        assert sign.return_annotation == self._context_type
        builder_func = cast(Callable[[BaseModel], Ctx], builder_func)

        self._storage[model] = builder_func
        return builder_func

    def setup(self) -> None:
        for path in self._discovery_paths:
            import_string(path)

        assert not any(builder is None for builder in self._storage.values())
        self._setup_done = True

    def build(self, data: dict[str, Any]) -> Ctx:
        assert self._setup_done

        for model, builder in self._storage.items():
            assert builder is not None
            try:
                obj = model(**data)
                return builder(obj)
            except ValidationError:
                pass
        raise InvalidScheme()
