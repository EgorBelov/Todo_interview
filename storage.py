#storage.py
from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import List

from models import Task


class StorageError(Exception):
    pass


class JsonTaskStorage:
    def __init__(self, file_path: Path):
        self.file_path = file_path

    def load(self) -> List[Task]:
        if not self.file_path.exists():
            # первый запуск: создаём пустое хранилище
            try:
                self.file_path.write_text("[]", encoding="utf-8")
            except OSError as e:
                raise StorageError("Не удалось создать tasks.json.") from e
            return []

        try:
            raw = self.file_path.read_text(encoding="utf-8").strip()
            if not raw:
                # файл есть, но пустой — считаем пустым списком
                return []

            data = json.loads(raw)
            if not isinstance(data, list):
                raise StorageError("Некорректный формат tasks.json: ожидался список.")

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
            raise StorageError("tasks.json повреждён или содержит невалидный JSON.") from e
        except OSError as e:
            raise StorageError("Ошибка чтения tasks.json.") from e
        except (TypeError, ValueError) as e:
            raise StorageError("Некорректные данные в tasks.json.") from e


    def save(self, tasks: List[Task]) -> None:
        try:
            data = [asdict(t) for t in tasks]
            tmp = self.file_path.with_suffix(".tmp")
            tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            tmp.replace(self.file_path)
        except OSError as e:
            raise StorageError("Ошибка сохранения tasks.json.") from e
