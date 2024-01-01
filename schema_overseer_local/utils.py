from importlib import import_module
from pkgutil import iter_modules


def import_string(import_path: str) -> None:
    module = import_module(import_path)

    if hasattr(module, '__path__'):  # it is a package
        for submodule_info in iter_modules(module.__path__):
            sub_path = f'{import_path}.{submodule_info.name}'
            import_string(sub_path)
