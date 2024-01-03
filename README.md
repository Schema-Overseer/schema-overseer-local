# Schema Overseer (local version)

Helper to create a compatibility layer between inputs in different formats and other parts of an application.

For multi-repository service see [schema-overseer-service](https://github.com/Schema-Overseer/schema-overseer-service)


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
class Output:
    value: int
    function: Callable  # <- output object can contain any python objects

schema_registry = SchemaRegistry(Output)
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
@schema_registry.add_builder
def old_builder(data: OldInputFormat) -> Output:
    return Output(
        value=data.value,
        func=my_function,
    )

@schema_registry.add_builder
def new_builder(data: NewInputFormat) -> Output:
    return Output(
        value=data.renamed_value,
        func=my_other_function,
    )
```

4. Use it in the application context
```python

schema_registry.setup()  # see "Discovery" chapter in documentation

def app(raw_data: dict[str, Any]):
    try:
        output = schema_registry.build(source_dict=raw_data)
    except InvalidScheme:
        pass  # Handle the exception

    # Use output
    output.func()
    return output.value

```

## Discovery and managing dependencies

TODO


## Strict self-check

TODO


## Object as a source

TODO


## Tutorial

Please refer to the tutorial, describing use case in details [here](TODO)
