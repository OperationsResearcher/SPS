# -*- coding: utf-8 -*-
"""Task status normalization helpers."""

STATUS_ALIASES = {
    'to do': 'Yapılacak',
    'todo': 'Yapılacak',
    'backlog': 'Yapılacak',
    'in progress': 'Devam Ediyor',
    'doing': 'Devam Ediyor',
    'done': 'Tamamlandı',
    'completed': 'Tamamlandı',
    'on hold': 'Beklemede',
    'blocked': 'Beklemede',
}

COMPLETED_STATUSES = ['Tamamlandı', 'Done', 'Completed']


def normalize_task_status(value):
    """Normalize task status values to the TR status set."""
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    key = text.lower()
    return STATUS_ALIASES.get(key, text)
