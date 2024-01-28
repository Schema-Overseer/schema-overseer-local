# Schema Overseer – Local

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen)](https://github.com/pre-commit/pre-commit)
[![GA test](https://github.com/Schema-Overseer/schema-overseer-local/actions/workflows/ci.yml/badge.svg)](https://github.com/Schema-Overseer/schema-overseer-local/actions)
[![PyPI](https://img.shields.io/pypi/v/schema-overseer-local)](https://pypi.org/project/schema-overseer-local/)
[![License](https://img.shields.io/pypi/l/schema-overseer-local)](./LICENSE)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/schema-overseer-local)](https://pypi.org/project/schema-overseer-local/)
[![PyPI - Format](https://img.shields.io/pypi/format/schema-overseer-local)](https://pypi.org/project/schema-overseer-local/)


*This is a local version of Schema Overseer, intended to use in a single repository. For the multi-repository service see [schema-overseer-service](https://github.com/Schema-Overseer/schema-overseer-service).*

**Schema Overseer** ensures strict adherence to defined data formats and raises an exception in case of attempting to process unsupported input schema.<br>
In more technical terms, it is an [adapter](https://en.wikipedia.org/wiki/Adapter_pattern) between inputs with different schema and other application components.

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
For quick start we will use single file, but in a real application it's better to use [multiple files](#using-miltiple-python-files).

2. Define the output schema you plan to work with.<br>
The output schema could be any object. For the tutorial purpose we will use `dataclass`. The output schema attributes could be any python objects, including non-serializables. Output could have the same behavior as the original input object, or a completely different one. Here is example of different behavior.

    ```python
    @dataclass
    class Output:
        value: int
        function: Callable
    ```

3. Create the `SchemaRegistry` instance for `Output`.

    ```python
    schema_registry = SchemaRegistry(Output)
    ```

4. Define the input schema using [pydantic](https://docs.pydantic.dev/) and register them in `schema_registry`.

    ```python
    @schema_registry.add_scheme
    class OldInputFormat(BaseModel):
        value: str

    @schema_registry.add_scheme
    class NewInputFormat(BaseModel):
        renamed_value: int
    ```

5. Implement builders - functions to convert each registered input to `Output`.<br>
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
        except InvalidSchemeError as error:
            raise MyApplicationError() from error  # handle the exception

        # use output object
        output.function()
        return output.value
    ```


Full quickstart example is [here](/tutorial/quickstart)<br>
Run it: `poetry run python -m tutorial.quickstart.app`


## FAQ

- **Q:** Why is this project exists? Isn't it too much overhead for such a simple task?<br>
  **A:** It depends on the scale of the different formats you need to support. In case of a few formats to support, `schema-overseer-local` would be an overhead indeed. But in the projects with lots of different formats, such extensive adapter layer could be helpful. Another goal of `schema-overseer-local` is to serve as a fast and simple introduction to `schema-overseer-service` for sophisticated use cases with multiple teams and repositories to work with.

- **Q:** How is this project better than an adapter I can code quickly myself?<br>
  **A:** `schema-overseer-local` has three important benefits:
    - it provides type checking;
    - it has very detailed runtime checks;
    - and it is easily extensible.

- **Q:** Why I have to use type hinting in builders?<br>
  **A:** `schema-overseer-local` uses the same pattern as `pydantic` and `FastAPI` for input and output validation in both runtime and static analysis. It provides an extra layer of defense against code errors. Even if your code is not entirely correctly typed or not checked with static analysis tools like [mypy](https://mypy-lang.org/), the data is still validated.


## Usage

### Using multiple Python files

TODO


### Discovery and managing dependencies

TODO


### Runtime safety and strict self-checks

TODO


### Object as a source

TODO


### Use one of the input scheme as output

TODO
