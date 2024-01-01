import datetime

from .models.new import NewPayload
from .models.old import OldPayload
from .registry import LogContext, payload_schema_registry


@payload_schema_registry.add_builder
def old_builder(payload: OldPayload) -> LogContext:
    return LogContext(
        log_entry=payload.query,
        log_datetime=datetime.datetime.now(),
    )


@payload_schema_registry.add_builder
def new_builder(payload: NewPayload) -> LogContext:
    text_log_entry = '<no text>' if payload.text is None else payload.text
    image_log_entry = 'empty' if payload.image is None else payload.image
    log_entry = f'{text_log_entry} | <image "{image_log_entry}">'

    return LogContext(
        log_entry=log_entry,
        log_datetime=payload.created_at or datetime.datetime.now(),
    )
