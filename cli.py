from __future__ import annotations

from typing import Optional

from service import TaskService
from storage import StorageError


class ConsoleUI:
    def __init__(self, service: TaskService):
        self.service = service

    def run(self) -> None:
        while True:
            self._print_menu()
            choice = input("Выберите действие: ").strip()

            try:
                if choice == "0":
                    print("👋 До встречи!")
                    return

                elif choice == "1":
                    title = input("Введите название задачи: ")
                    task = self.service.add_task(title)
                    print(f"✅ Добавлено: {task.title}")

                elif choice == "2":
                    task = self._choose_task("удалить")
                    if task:
                        deleted = self.service.delete_task(task.id)
                        print(f"🗑️  Удалено: {deleted.title}")

                elif choice == "3":
                    task = self._choose_task("отметить выполненной")
                    if task:
                        done = self.service.mark_done(task.id)
                        if done.done:
                            print(f"🎉 Выполнено: {done.title}")

                elif choice == "4":
                    self._print_tasks()

                elif choice == "5":
                    self._edit_task()

                else:
                    print("❌ Неизвестная команда. Введите число из меню (0–5).")

            except ValueError as e:
                print(f"❌ {e}")
            except KeyError as e:
                print(f"❌ {e}")
            except StorageError as e:
                print(f"⚠️  {e}")
            except Exception as e:
                print(f"❌ Непредвиденная ошибка: {e}")

    def _print_menu(self) -> None:
        print(
            "\n=== ToDo: консольный менеджер задач ===\n"
            "1) Добавить задачу\n"
            "2) Удалить задачу\n"
            "3) Отметить задачу выполненной\n"
            "4) Показать список задач\n"
            "5) Изменить задачу\n"
            "0) Выход\n"
        )

    def _print_tasks(self) -> None:
        tasks = self.service.list_tasks()
        if not tasks:
            print("📭 Список задач пуст.")
            return

        print("\nВаши задачи:")
        for i, t in enumerate(tasks, start=1):
            status = "✅" if t.done else "⏳"
            created = f" (создано: {t.created_at})" if t.created_at else ""
            print(f"  {i}) {status} {t.title}{created}")
        print()

    def _choose_task(self, action: str):
        """
        Выбор задачи по НОМЕРУ в текущем списке (1..N).
        ID пользователю не показываем.
        """
        tasks = self.service.list_tasks()
        if not tasks:
            print("📭 Список задач пуст.")
            return None

        self._print_tasks()
        num = self._read_int(f"Введите номер задачи, чтобы {action} (или Enter — отмена): ", allow_empty=True)
        if num is None:
            print("↩️  Отменено.")
            return None

        if not (1 <= num <= len(tasks)):
            print("❌ Неверный номер.")
            return None

        return tasks[num - 1]

    def _edit_task(self) -> None:
        task = self._choose_task("изменить")
        if not task:
            return

        print(
            "\nЧто изменить?\n"
            "1) Переименовать\n"
            "2) Переключить выполнено/не выполнено\n"
            "0) Отмена\n"
        )
        choice = input("Выберите действие: ").strip()

        if choice == "0":
            print("↩️  Отменено.")
            return

        if choice == "1":
            new_title = input("Введите новое название: ").strip()
            if not new_title:
                print("❌ Новое название не может быть пустым.")
                return
            updated = self.service.update_title(task.id, new_title)
            print(f"✏️  Обновлено: {updated.title}")

        elif choice == "2":
            updated = self.service.toggle_done(task.id)
            state = "выполнена ✅" if updated.done else "не выполнена ⏳"
            print(f"🔁 Статус изменён: {updated.title} — {state}")

        else:
            print("❌ Неизвестная команда.")

    @staticmethod
    def _read_int(prompt: str, allow_empty: bool = False) -> Optional[int]:
        raw = input(prompt).strip()
        if not raw:
            return None if allow_empty else None
        try:
            return int(raw)
        except ValueError:
            print("❌ Ожидалось целое число.")
            return None
