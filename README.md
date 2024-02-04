# Schema Overseer – Local

[![PyPI](https://img.shields.io/pypi/v/schema-overseer-local)](https://pypi.org/project/schema-overseer-local/)
[![License](https://img.shields.io/pypi/l/schema-overseer-local)](./LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/schema-overseer-local)](https://pypi.org/project/schema-overseer-local/)
[![Github Actions CI](https://github.com/Schema-Overseer/schema-overseer-local/actions/workflows/ci.yml/badge.svg)](https://github.com/Schema-Overseer/schema-overseer-local/actions)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen)](https://github.com/pre-commit/pre-commit)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

> This is a local version of Schema Overseer, intended to use in a single repository.<br>
> For the multi-repository service see [schema-overseer-service](https://github.com/Schema-Overseer/schema-overseer-service).

**Schema Overseer** ensures strict adherence to defined data formats and raises an exception in case of attempting to process unsupported input schema.<br>
In more technical terms, it is an adapter[^1] between inputs with different schemas and other application components.


#### Why is it important?
- Data formats evolve over time
- Developers need to simultaneously support both legacy and new data formats
- Mismatches between input data format and the corresponding code can lead to unexpected and hard-to-debug runtime errors
- As the number of supported data formats increases, application code often becomes less maintainable

#### Features
- Straightforward extensibility
- Static analysis checks via type checking
- Detailed runtime checks
- Incoming data validation with [pydantic](https://docs.pydantic.dev/)


## Use Cases and Tutorials

1. [Maintain multiple version of external-facing API](/tutorial)

2. [Manage metadata for different Machine Learning models](TODO)


## Installation

```bash
pip install schema-overseer-local
```

## Quick Start

1. Create a file `adapter.py` to define the adapter logic.<br>
For quick start we will use single file, but in a real application it's better to use [multiple files](#using-multiple-python-files).

2. **Output**. Define the output schema you plan to work with.<br>
The output schema could be any object. For the tutorial purpose we will use `dataclass`. The output schema attributes could be any python objects, including non-serializables. Output could have the same behavior as the original input object, or a completely different one. Here is example of different behavior.

    ```python
    @dataclass
    class Output:
        value: int
        function: Callable
    ```

3. **Registry**. Create the `SchemaRegistry` instance for `Output`.

    ```python
    schema_registry = SchemaRegistry(Output)
    ```

4. **Input schemas**. Define the input schemas using [pydantic](https://docs.pydantic.dev/) and register them in `schema_registry`.

    ```python
    @schema_registry.add_schema
    class OldInputFormat(BaseModel):
        value: str

    @schema_registry.add_schema
    class NewInputFormat(BaseModel):
        renamed_value: int
    ```

5. **Builders**. Implement functions to convert each registered input to `Output`.<br>
Builders require type hinting to link input formats and `Output`.

    ```python
    @schema_registry.add_builder
    def old_builder(data: OldInputFormat) -> Output:
        return Output(
            value=data.value,
            function=my_function,
        )

    @schema_registry.add_builder
    def new_builder(data: NewInputFormat) -> Output:
        return Output(
            value=data.renamed_value,
            function=my_other_function,
        )
    ```

6. Finally, use `schema_registry` inside the application to get validated output or handle the exception.

    ```python
    schema_registry.setup()  # see "Discovery" chapter in documentation

    def my_service(raw_data: dict[str, Any]):
        try:
            output = schema_registry.build(source_dict=raw_data)  # build output object
        except BuildError as error:
            raise MyApplicationError() from error  # handle the exception

        # use output object
        output.function()
        return output.value
    ```


Full quickstart example is [here](/tutorial/quickstart)<br>
Run it:
```bash
git clone git@github.com:Schema-Overseer/schema-overseer-local.git
cd schema-overseer-local
poetry install
poetry run python -m tutorial.quickstart.app
```


## Usage

### Using multiple Python files

While you can define registry, models and builders in one or two files, it is usually a better idea to split them into different files, i.e., Python modules.

There are different ways to do the file structure, we recommend one of the following:

- Minimal — start with this one, when you are still figuring out the best way to work
- Expanded builders — useful for the case with lots of code for each builder
- Detached output — useful for the case, when the output is a big or complex entity

<table><tr><td valign="top">
Minimal

```
├── __init__.py
├── builders.py
├── models
│   ├── __init__.py
│   ├── v1.py
│   ├── v2.py
│   ├── ...
│   └── vN.py
└── registry.py
```
</td><td valign="top">
Expanded builders

```
├── __init__.py
├── builders
│   ├── __init__.py
│   ├── v1.py
│   ├── v2.py
│   ├── ...
│   └── vN.py
├── models
│   ├── __init__.py
│   ├── v1.py
│   ├── v2.py
│   ├── ...
│   └── vN.py
└── registry.py
```
</td><td valign="top">
Detached output

```
├── __init__.py
├── builders.py
├── models
│   ├── __init__.py
│   ├── v1.py
│   ├── v2.py
│   ├── ...
│   └── vN.py
├── output.py
└── registry.py
```
</td></tr></table>

Models (i.e., input data formats) are decoupled first for two reasons:
 * If models contain inner models inside, it would be harder to distinguish between inner models for different root models. (see [Q](#q-should-i-re-use-inner-pydantic-models-in-different-data-formats))
 * If you transition to [schema-overseer-service](https://github.com/Schema-Overseer/schema-overseer-service), the models are sourced from the outside of your code, so this split will come naturally.


### Load modules automatically

> [!NOTE]
> Python will not load modules automatically, unless they are explicitly imported.<br>
> `SchemaRegistry` has a `discovery_paths: Sequence[str]` argument to load all required models.<br>
> Specified modules and packages will be loaded at `SchemaRegistry.setup()`. <br>

Definition (`SchemaRegistry(...)`) is decoupled with loading (`SchemaRegistry.setup()`) to prevent cycle imports, that's why calling `setup()` is required.

Argument `discovery_paths` takes a sequence of strings in the absolute import format. Entries could be either python modules (single files) or python packages (folder with `__init__.py` and other `*.py` files inside)

For example, this will work for minimal option, mentioned above:
```python
schema_registry = SchemaRegistry(
    Output,
    discovery_paths=[
        'example_project.payload.models',  # loaded as package
        'example_project.payload.builders',  # loaded as module
    ],
)
```


### Runtime safety and strict self-checks

In addition to static type hint checks, `schema-overseer-local` performs runtime checks to ensure:
* Each registered model has only one corresponding builder.
* All builders have a proper call signature, which includes:
    * One argument for the input data
    * No additional non-default arguments
* All builders have proper type hints

Additional runtime checks:
* If set to `validate_output=True` (the default is `False`), it verifies whether the builder returns an object of the annotated type using pydantic.
* By default, `schema-overseer-local` selects the builder from the first valid schema. However, if `check_for_single_valid_schema=True` is enabled, it ensures only one schema is valid for the input data.<br>
If multiple schemas are found to be valid, a `MultipleValidSchemasError` will be raised.


### Object as a source

`SchemaRegistry.build()` method operates in two modes:
  * Using dict-like objects as inputs and extracting fields with `__getitem__`<br>
    Use `build(source_dict=...)` for this option
  * Using objects with data as attributes and extracting fields with `getattr`<br>
    Use `build(source_object=...)` for this option

`source_dict` and `source_object` are mutually exclusive.

### Use one of the input schema as output

TODO


## FAQ

#### Q: Why is this project exists? Isn't it too much overhead for such a simple task?
  **A:** It depends on the scale of the different formats you need to support. In case of a few formats to support, `schema-overseer-local` would be an overhead indeed. But in the projects with lots of different formats, such extensive adapter layer could be helpful. Another goal of `schema-overseer-local` is to serve as a fast and simple introduction to `schema-overseer-service` for sophisticated use cases with multiple teams and repositories to work with.

#### Q: How is this project better than an adapter I can code quickly myself?
  **A:** `schema-overseer-local` has three important benefits:
    - it provides type checking;
    - it has very detailed runtime checks;
    - and it is easily extensible.

#### Q: Why I have to use type hinting in builders?
  **A:** `schema-overseer-local` uses the same pattern as `pydantic` and `FastAPI` for input and output validation in both runtime and static analysis. It provides an extra layer of defense against code errors. Even if your code is not entirely correctly typed or not checked with static analysis tools like [mypy](https://mypy-lang.org/), the data is still validated.

#### Q: Should I re-use inner pydantic models in different data formats?

<details><summary>Code example</summary>

```python
class InnerModel(BaseModel):
    value: int


class InputFormatV1(BaseModel):
    inner: InnerModel
```
```python
class InnerModelV2(BaseModel):
    value: int


class InputFormatV2(BaseModel):
    inner: InnerModelV2  # or re-use InnerModel?
```
</details>

  **A:** Not really. While it might be tempting to adhere to the DRY[^2] principle in this context, it's generally a better approach to fully separate nested pydantic models into distinct modules, avoiding their reuse even if they are identical.<br>
  The primary rationale is future code maintainability: tracking modifications in reused models can be challenging, and the introduction of a new format version could require changes to the inner model, which would then demand separation regardless.

[^1]: [Adapter pattern](https://en.wikipedia.org/wiki/Adapter_pattern)
[^2]: [Don't repeat yourself](https://en.wikipedia.org/wiki/Don%27t_repeat_yourself)
