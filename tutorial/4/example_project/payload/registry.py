import datetime
from dataclasses import dataclass
from schema_overseer_local import SchemaRegistry

@dataclass
class LogContext:
    log_entry: int
    log_datetime: datetime.datetime


payload_schema_registry = SchemaRegistry(
    "payload",
    LogContext,
    discovery_path=[
        "example_project.payload.models",
        "example_project.payload.builders",
    ],
)
