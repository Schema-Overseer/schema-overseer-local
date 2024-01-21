# Schema Overseer – Local

*This is a local version of Schema Overseer, intented to use in a single repository. For the multi-repository service see [schema-overseer-service](https://github.com/Schema-Overseer/schema-overseer-service).*

Schema Overseer addresses a crucial challenge with data formats synchronization, such as schemas or configurations:
- Data formats evolve over time;
- In software development, the need to simultaneously support both legacy and new data formats is widespread.
- Mismatches between input data format and the corresponding code can lead to unexpected and hard-to-debug runtime errors.
- As the number of supported data formats increases, application code often becomes less maintainable.

Schema Overseer ensures strict adherence to defined data formats and raises an error in case of attempting to process unsupported input schemas.

In more technical terms, Schema Overseer helps to create an [adapter](https://en.wikipedia.org/wiki/Adapter_pattern) between inputs with different schemas and other components within an application.

## Features

- it has very detailed runtime checks;
    - it provides type checking; / Type hinting validation
    - and it is easily extensible.
- A convenient place to verify incoming data and convert to a specific format


## Use Cases and Tutorials

1. **Manage metadata for different Machine Learning models:** TODO

2. **Maintain multiple version of external-facting API:** TODO

## Installation

```bash
pip install schema-overseer-local
```

## Quick Start

1. Create a file `adapter.py` to define the adapter logic. For better practices, consider using [multiple files](#Using-miltiple-Python-files).

2. Define the output schema you plan to work with. <br>
The output schema could be anything, but we will use `dataclass` as a good practice. Attributes in the output can be any python objects, including non-serializables. Output can be designed with the same behaviour as the original input object, or with a completely different.

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

5. Implement builders - functions to convert each registered input to `Output`. <br> Builders require type hinting to link input formats and `Output`.

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

6. Finally, use `schema_registry` in application to get validated output or handle the exception.

    <details>

    <summary>Show code</summary>

    ```python
    schema_registry.setup()  # see "Discovery" chapter in documentation

    def app(raw_data: dict[str, Any]):
        try:
            output = schema_registry.build(source_dict=raw_data)  # build output object
        except InvalidScheme as error:
            raise MyApplicationError() from error  # handle the exception

        # use output object
        output.func()
        return output.value

    ```

    </details>

7. See the full working example:

    <details>

    <summary>Show code</summary>

    TODO

    ```python
    ```

    </details>


## FAQ



- **Q:** Why is this project exists? Isn't it too much overhead for a such simple task?<br>
**A:** The main goal of `schema-overseer-local` is to serve as a fast and simple introduction to `schema-overseer-service`.

- **Q:** How is this project better than an adapter I can code in an hour? <br>
**A:** `schema-overseer-local` has three important benefits:
    - it has very detailed runtime checks;
    - it provides type checking;
    - and it is easily extensible.

- **Q:** Why does `SchemaRegistry` use type hinting in runtime?
**A:** `schema-overseer-local` uses the same pattern as `pydantic` and `FastAPI` for input and output validation in both runtime and static analysis stages.
**A:** `schema-overseer-local` uses the type hinting at runtime to ensure
 same pattern as `pydantic` and `FastAPI` for input and output validation in both runtime and static analysis stages.

## Usage

### Using miltiple Python files

TODO


### Discovery and managing dependencies

TODO


### Runtime safety and strict self-checks

TODO


### Object as a source

TODO


### Use one of the input scheme as output

TODO