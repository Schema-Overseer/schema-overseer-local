import datetime
from dataclasses import dataclass
from schema_overseer_local import SchemaRegistry


@dataclass
class LogContext:
    log_entry: str
    log_datetime: datetime.datetime


payload_schema_registry = SchemaRegistry(
    LogContext,
    discovery_paths=[
        'example_project.payload.models',
        'example_project.payload.builders',
    ],
)
