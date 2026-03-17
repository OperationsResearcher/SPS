# -*- coding: utf-8 -*-
"""Lightweight telemetry helpers for critical flows."""

from datetime import datetime


def log_event(logger, event_name, **payload):
    if not logger:
        return
    data = {
        'event': event_name,
        'timestamp': datetime.utcnow().isoformat() + 'Z',
    }
    data.update(payload or {})
    logger.info(f"telemetry={data}")
