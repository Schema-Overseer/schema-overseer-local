#!/usr/bin/env python
from __future__ import annotations

from typing import Any

from schema_overseer_local import InvalidSchemeError

from .adapter import schema_registry

schema_registry.setup()  # see "Discovery" chapter in documentation


def my_service(raw_data: dict[str, Any]) -> int:
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
    data: dict[str, Any]
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
