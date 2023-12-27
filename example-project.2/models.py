from typing import Callable

from dataclasses import dataclass

@dataclass
class ApplicationContext:
    my_var: int
    preprocessing: Callable[[...], ...]


schema_registry = SchemaRegistry('model_config', ApplicationContext, discovery_path=['example_project.builders'])
