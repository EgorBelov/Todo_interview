#app.py
from pathlib import Path

from cli import ConsoleUI
from service import TaskService
from storage import JsonTaskStorage, StorageError

DATA_FILE = Path("tasks.json")


def main() -> int:
    try:
        storage = JsonTaskStorage(DATA_FILE)
        service = TaskService(storage)
        ui = ConsoleUI(service)
        ui.run()
        return 0
    except StorageError as e:
        print(f"⚠️  {e}")
        return 1
    except KeyboardInterrupt:
        print("\n👋 Завершено пользователем (Ctrl+C).")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
