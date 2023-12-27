
from .schema import resolve_scheme, UnexpectedScheme

def main(config: dict):
    try:
        context = resolve_scheme(config)
    except UnexpectedScheme:
        print('bad config')
    else:
        print('Config parsed successfully')

    config.my_var
