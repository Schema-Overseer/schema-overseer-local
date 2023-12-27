
from .schema import resolve_scheme, UnexpectedScheme
from .models import schema_registry
from fastapi import FastAPI


def main(config: dict):
    schema_registry.setup()

    try:
        context = schema_registry.build(config)
    except UnexpectedScheme:
        print('bad config')
    else:
        print('Config parsed successfully')

    config.my_var
