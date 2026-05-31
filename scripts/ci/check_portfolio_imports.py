#!/usr/bin/env python3
"""Portföy modelleri yalnızca app.models.portfolio_project üzerinden import edilmeli."""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

WATCH_DIRS = [
    ROOT / "micro" / "modules" / "proje",
    ROOT / "micro" / "modules" / "kurum",
    ROOT / "micro" / "modules" / "masaustu",
]
WATCH_FILES = [
    ROOT / "main" / "routes.py",
    ROOT / "api" / "routes.py",
]

PORTFOLIO_SYMBOLS = (
    "Project",
    "Task",
    "ProjectFile",
    "RaidItem",
    "TimeEntry",
    "TaskActivity",
    "TaskImpact",
    "TaskComment",
    "TaskMention",
    "ProjectRisk",
    "project_members",
    "project_leaders",
    "project_observers",
    "project_related_processes",
    "task_predecessors",
)
SYMBOLS_RE = "|".join(re.escape(s) for s in PORTFOLIO_SYMBOLS)
FORBIDDEN = re.compile(rf"from\s+models\s+import\s+[^\n#]*\b({SYMBOLS_RE})\b")

errors: list[str] = []
paths = list(WATCH_FILES)
for d in WATCH_DIRS:
    paths.extend(sorted(d.glob("**/*.py")))

for path in paths:
    if not path.is_file():
        continue
    for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if FORBIDDEN.search(line):
            errors.append(f"{path.relative_to(ROOT).as_posix()}:{i}: {line.strip()}")

if errors:
    print("YASAK: portföy modelleri 'from models import ...' ile alınamaz:")
    for e in errors:
        print(f"  - {e}")
    sys.exit(1)

print("OK: portfolio_project import politikası")
