#todo.py
from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional


DATA_FILE = Path("tasks.json")


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
            title=title,
            done=False,
            created_at=datetime.now().isoformat(timespec="seconds"),
        )


class StorageError(Exception):
    pass


class TaskStorage:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def load(self) -> List[Task]:
        if not self.file_path.exists():
            return []

        try:
            raw = self.file_path.read_text(encoding="utf-8").strip()
            if not raw:
                return []
            data = json.loads(raw)
            if not isinstance(data, list):
                raise StorageError("Некорректный формат файла: ожидался список задач.")

            tasks: List[Task] = []
            for item in data:
                if not isinstance(item, dict):
                    continue

                if "id" not in item or "title" not in item:
                    continue
                tasks.append(
                    Task(
                        id=int(item["id"]),
                        title=str(item["title"]),
                        done=bool(item.get("done", False)),
                        created_at=str(item.get("created_at", "")),
                    )
                )
            return tasks
        except json.JSONDecodeError as e:
            raise StorageError(
                "Не удалось прочитать tasks.json: файл повреждён или содержит невалидный JSON."
            ) from e
        except OSError as e:
            raise StorageError("Ошибка чтения файла tasks.json.") from e
        except ValueError as e:
            raise StorageError("Некорректные данные в tasks.json.") from e

    def save(self, tasks: List[Task]) -> None:
        try:
            data = [asdict(t) for t in tasks]
            tmp = self.file_path.with_suffix(".json.tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self.file_path)
        except OSError as e:
            raise StorageError("Ошибка сохранения файла tasks.json.") from e


class TodoApp:
    def __init__(self, storage: TaskStorage):
        self.storage = storage
        self.tasks: List[Task] = []
        self._load()

    def _load(self) -> None:
        try:
            self.tasks = self.storage.load()
        except StorageError as e:
            print(f"⚠️  {e}")
            print("Файл будет проигнорирован, начнём с пустого списка задач.")
            self.tasks = []

    def _persist(self) -> None:
        try:
            self.storage.save(self.tasks)
        except StorageError as e:
            print(f"⚠️  {e}")
            print("Изменения не сохранены.")

    def _next_id(self) -> int:
        return (max((t.id for t in self.tasks), default=0) + 1)

    def add_task(self, title: str) -> None:
        title = title.strip()
        if not title:
            print("❌ Название задачи не может быть пустым.")
            return

        task = Task.new(self._next_id(), title)
        self.tasks.append(task)
        self._persist()
        print(f"✅ Задача добавлена: [{task.id}] {task.title}")

    def list_tasks(self) -> None:
        if not self.tasks:
            print("📭 Список задач пуст.")
            return

        print("\nВаши задачи:")
        for t in sorted(self.tasks, key=lambda x: x.id):
            status = "✅" if t.done else "⏳"
            created = f" (создано: {t.created_at})" if t.created_at else ""
            print(f"  {status} [{t.id}] {t.title}{created}")
        print()

    def find_task(self, task_id: int) -> Optional[Task]:
        for t in self.tasks:
            if t.id == task_id:
                return t
        return None

    def delete_task(self, task_id: int) -> None:
        task = self.find_task(task_id)
        if not task:
            print(f"❌ Задача с id={task_id} не найдена.")
            return

        self.tasks = [t for t in self.tasks if t.id != task_id]
        self._persist()
        print(f"🗑️  Задача удалена: [{task_id}] {task.title}")

    def mark_done(self, task_id: int) -> None:
        task = self.find_task(task_id)
        if not task:
            print(f"❌ Задача с id={task_id} не найдена.")
            return
        if task.done:
            print(f"ℹ️  Задача уже отмечена как выполненная: [{task_id}] {task.title}")
            return

        task.done = True
        self._persist()
        print(f"🎉 Готово! Задача выполнена: [{task_id}] {task.title}")

    def menu(self) -> None:
        print(
            "\n=== ToDo: консольный менеджер задач ===\n"
            "1) Добавить задачу\n"
            "2) Удалить задачу\n"
            "3) Отметить задачу выполненной\n"
            "4) Показать список задач\n"
            "0) Выход\n"
        )

    def run(self) -> None:
        while True:
            self.menu()
            choice = input("Выберите действие: ").strip()

            if choice == "0":
                print("👋 До встречи!")
                return

            if choice == "1":
                title = input("Введите название задачи: ")
                self.add_task(title)

            elif choice == "2":
                task_id = self._read_int("Введите id задачи для удаления: ")
                if task_id is not None:
                    self.delete_task(task_id)

            elif choice == "3":
                task_id = self._read_int("Введите id задачи для отметки выполненной: ")
                if task_id is not None:
                    self.mark_done(task_id)

            elif choice == "4":
                self.list_tasks()

            else:
                print("❌ Неизвестная команда. Введите число из меню (0–4).")

    @staticmethod
    def _read_int(prompt: str) -> Optional[int]:
        raw = input(prompt).strip()
        if not raw:
            print("❌ Значение не введено.")
            return None
        try:
            value = int(raw)
            if value <= 0:
                print("❌ id должен быть положительным числом.")
                return None
            return value
        except ValueError:
            print("❌ Ожидалось целое число.")
            return None


def main() -> int:
    app = TodoApp(TaskStorage(DATA_FILE))
    try:
        app.run()
        return 0
    except KeyboardInterrupt:
        print("\n👋 Завершено пользователем (Ctrl+C).")
        return 0
    except Exception as e:

        print(f"❌ Непредвиденная ошибка: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
