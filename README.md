# Schema Overseer (local version)

Schema compatibility manager for local repository.
For multi-repository service see [schema-overseer-service](https://github.com/Schema-Overseer/schema-overseer-service)

## Use case

This is a small helper to create compatibility layer between inputs in different formats and other parts of application.

## Installation

```bash
pip install schema-overseer-local
```

## Usage

1. Define the registry instance:

```python
from typing import Callable
from dataclasses import dataclass
from schema_overseer_local import SchemaRegistry

@dataclass
class ApplicationContext:
    value: int
    function: Callable


schema_registry = SchemaRegistry(ApplicationContext)
```

2. Define input schema using [pydantic](https://docs.pydantic.dev/) and register them
```python
from pydantic import BaseModel


@schema_registry.add_scheme
class OldInputFormat(BaseModel):
    value: str


@schema_registry.add_scheme
class NewInputFormat(BaseModel):
    renamed_value: int
```


3. Implement builders - function to convert each registered input to a output object
```python

@payload_schema_registry.add_builder
def old_builder(data: OldInputFormat) -> ApplicationContext:
    return ApplicationContext(
        value=data.value,
        func: my_function,
    )

@payload_schema_registry.add_builder
def new_builder(data: NewInputFormat) -> ApplicationContext:
    return ApplicationContext(
        value=data.renamed_value,
        func: my_other_function,
    )
```

4. Use it in the application context
```python

schema_registry.setup()

def app(raw_data: dict[str, Any]):
    try:
        context = schema_registry.build(source_dict=raw_data)
    except InvalidScheme:
        return Response("Invalid payload scheme", status=400)

    print(context.value)
    context.func()

```
## Tutorial

Please refer to the tutorial, describing use case in details [here]
