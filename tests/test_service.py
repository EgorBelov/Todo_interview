import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from service import TaskService
from storage import JsonTaskStorage


class TestTaskService(unittest.TestCase):
    def setUp(self) -> None:
        # каждому тесту — свой временный tasks.json
        self.tmp_dir = TemporaryDirectory()
        self.data_file = Path(self.tmp_dir.name) / "tasks.json"
        self.storage = JsonTaskStorage(self.data_file)
        self.service = TaskService(self.storage)

    def tearDown(self) -> None:
        self.tmp_dir.cleanup()

    def test_add_task_assigns_incremental_ids(self):
        t1 = self.service.add_task("Помыть посуду")
        t2 = self.service.add_task("Купить молоко")
        self.assertEqual(t1.id, 1)
        self.assertEqual(t2.id, 2)
        self.assertFalse(t1.done)
        self.assertTrue(self.data_file.exists(), "После add_task файл должен сохраниться")

    def test_list_tasks_sorted_unfinished_first_then_by_id(self):
        a = self.service.add_task("A")
        b = self.service.add_task("B")
        c = self.service.add_task("C")

        # пометим B выполненной
        self.service.mark_done(b.id)

        tasks = self.service.list_tasks()
        # ожидаем: A (todo), C (todo), B (done)
        self.assertEqual([t.title for t in tasks], ["A", "C", "B"])
        self.assertEqual([t.done for t in tasks], [False, False, True])

    def test_mark_done_sets_done_true(self):
        t = self.service.add_task("Задача")
        self.assertFalse(self.service.find(t.id).done)
        self.service.mark_done(t.id)
        self.assertTrue(self.service.find(t.id).done)

    def test_delete_task_removes_task(self):
        t1 = self.service.add_task("One")
        t2 = self.service.add_task("Two")

        deleted = self.service.delete_task(t1.id)
        self.assertEqual(deleted.title, "One")
        self.assertIsNone(self.service.find(t1.id))
        self.assertIsNotNone(self.service.find(t2.id))

    def test_update_title_validates_and_updates(self):
        t = self.service.add_task("Old")
        updated = self.service.update_title(t.id, "New title")
        self.assertEqual(updated.title, "New title")

        with self.assertRaises(ValueError):
            self.service.update_title(t.id, "   ")

    def test_toggle_done_flips_state(self):
        t = self.service.add_task("X")
        self.assertFalse(self.service.find(t.id).done)

        self.service.toggle_done(t.id)
        self.assertTrue(self.service.find(t.id).done)

        self.service.toggle_done(t.id)
        self.assertFalse(self.service.find(t.id).done)


if __name__ == "__main__":
    unittest.main()
