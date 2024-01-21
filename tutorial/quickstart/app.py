#!/usr/bin/env python
from typing import Any, Dict

from schema_overseer_local import InvalidSchemeError

from adapter import schema_registry

schema_registry.setup()  # see "Discovery" chapter in documentation


def my_service(raw_data: Dict[str, Any]):
    try:
        output = schema_registry.build(source_dict=raw_data)  # build output object
    except InvalidSchemeError as error:
        raise MyApplicationError() from error  # handle the exception

    # use output object
    output.function()
    return output.value


class MyApplicationError(Exception):
    pass


if __name__ == '__main__':
    data = {'value': '1'}
    print(f'Input: {data}')
    result = my_service(data)
    print(f'Result: {result}\n')

    data = {'renamed_value': 2}
    print(f'Input: {data}')
    result = my_service(data)
    print(f'Result: {result}\n')

    data = {'some_other_key': None}
    print(f'Input: {data}')
    try:
        result = my_service(data)
    except MyApplicationError:
        print('Error: invalid input')
    else:
        print(f'Result: {result}\n')
