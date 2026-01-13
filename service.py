from __future__ import annotations

import re
from difflib import SequenceMatcher
from typing import List, Optional, Tuple

from models import Task
from storage import JsonTaskStorage


class TaskService:
    def __init__(self, storage: JsonTaskStorage):
        self.storage = storage
        self.tasks: List[Task] = self.storage.load()

    def _persist(self) -> None:
        self.storage.save(self.tasks)

    def _next_id(self) -> int:
        return max((t.id for t in self.tasks), default=0) + 1

    def list_tasks(self, done: Optional[bool] = None) -> List[Task]:
        """
        done=None  -> все задачи
        done=True  -> только выполненные
        done=False -> только невыполненные

        Сортировка: сначала невыполненные, потом выполненные, внутри по id.
        """
        tasks = self.tasks
        if done is not None:
            tasks = [t for t in tasks if t.done == done]

        return sorted(tasks, key=lambda t: (t.done, t.id))  # False < True

    def set_done(self, task_id: int, done: bool) -> Task:
        task = self.find(task_id)
        if not task:
            raise KeyError(f"Задача с id={task_id} не найдена.")
        task.done = done
        self._persist()
        return task

    def add_task(self, title: str) -> Task:
        title = title.strip()
        if not title:
            raise ValueError("Название задачи не может быть пустым.")
        task = Task.new(self._next_id(), title)
        self.tasks.append(task)
        self._persist()
        return task

    def find(self, task_id: int) -> Optional[Task]:
        return next((t for t in self.tasks if t.id == task_id), None)

    def delete_task(self, task_id: int) -> Task:
        task = self.find(task_id)
        if not task:
            raise KeyError(f"Задача с id={task_id} не найдена.")
        self.tasks = [t for t in self.tasks if t.id != task_id]
        self._persist()
        return task

    def mark_done(self, task_id: int) -> Task:
        task = self.find(task_id)
        if not task:
            raise KeyError(f"Задача с id={task_id} не найдена.")
        if task.done:
            return task
        task.done = True
        self._persist()
        return task

    def update_title(self, task_id: int, new_title: str) -> Task:
        new_title = new_title.strip()
        if not new_title:
            raise ValueError("Новое название не может быть пустым.")
        task = self.find(task_id)
        if not task:
            raise KeyError(f"Задача не найдена.")
        task.title = new_title
        self._persist()
        return task

    def toggle_done(self, task_id: int) -> Task:
        task = self.find(task_id)
        if not task:
            raise KeyError(f"Задача не найдена.")
        task.done = not task.done
        self._persist()
        return task

    def search_tasks(self, query: str, limit: int = 7, cutoff: float = 0.55) -> List[Tuple[Task, float]]:
        """
        Возвращает список (task, score) по убыванию score.
        Учитывает:
        - точное вхождение подстроки (с бонусом)
        - похожесть строк (SequenceMatcher), помогает при опечатках
        """
        q = query.strip().lower()
        if not q:
            return []

        scored: List[Tuple[Task, float]] = []
        for t in self.tasks:
            title = t.title.lower()

            # базовая похожесть
            score = SequenceMatcher(a=q, b=title).ratio()

            # бонус за подстроку (часть названия)
            if q in title:
                score = max(score, 0.9)  # почти “точное” попадание

            if score >= cutoff:
                scored.append((t, score))

        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]
