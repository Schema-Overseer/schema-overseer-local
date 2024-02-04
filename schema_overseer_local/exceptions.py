class SetupError(Exception):
    """Could be raised during registration of schema or builders, or during SchemaRegistry.setup()"""


class BuildError(Exception):
    """Could be raised in runtime during SchemaRegistry.build()"""


class NoMatchingSchemaError(BuildError):
    """Raised if not input schema was matched during SchemaRegistry.build()"""


class OutputValidationError(BuildError):
    """Raise when output validation failed during SchemaRegistry.build()"""


class MultipleValidSchemasError(BuildError):
    """Raised when more than one input schema was matched during SchemaRegistry.build()"""
