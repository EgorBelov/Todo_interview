from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Task:
    id: int
    title: str
    done: bool = False
    created_at: str = ""

    @staticmethod
    def new(task_id: int, title: str) -> "Task":
        return Task(
            id=task_id,
            title=title.strip(),
            done=False,
            created_at=datetime.now().isoformat(timespec="seconds"),
        )
