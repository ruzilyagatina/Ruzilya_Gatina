import unittest
import os
import sys
import tkinter as tk

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from main import ExpenseTracker, DATA_FILE

class TestExpenseTracker(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = ExpenseTracker(self.root)
        self.app.expenses = []
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        self.app.save_data()

    def tearDown(self):
        self.root.destroy()
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)

    # Позитивные тесты
    def test_validate_valid_amount(self):
        self.assertEqual(self.app._validate_amount("150.75"), (150.75, None))
        self.assertEqual(self.app._validate_amount("10,50"), (10.5, None))

    def test_validate_valid_date(self):
        d, err = self.app._validate_date("2024-02-29") # Високосный год
        self.assertIsNotNone(d)
        self.assertIsNone(err)

    def test_filter_by_category(self):
        self.app.expenses = [
            {"amount": 100, "category": "Еда", "date": "2024-01-10"},
            {"amount": 200, "category": "Транспорт", "date": "2024-01-15"}
        ]
        self.app.filter_cat.set("Еда")
        self.app.apply_filters()
        total = float(self.total_label.cget("text").replace(" ₽", ""))
        self.assertEqual(total, 100.00)

    def test_filter_by_date_range(self):
        self.app.expenses = [
            {"amount": 50, "category": "Еда", "date": "2024-01-01"},
            {"amount": 150, "category": "Еда", "date": "2024-01-20"},
            {"amount": 300, "category": "Еда", "date": "2024-02-10"}
        ]
        self.app.date_start.delete(0, tk.END); self.app.date_start.insert(0, "2024-01-10")
        self.app.date_end.delete(0, tk.END); self.app.date_end.insert(0, "2024-01-25")
        self.app.apply_filters()
        total = float(self.total_label.cget("text").replace(" ₽", ""))
        self.assertEqual(total, 150.00)

    # Негативные тесты
    def test_validate_negative_amount(self):
        val, err = self.app._validate_amount("-100")
        self.assertIsNone(val)
        self.assertIn("положительным", err)

    def test_validate_zero_amount(self):
        val, err = self.app._validate_amount("0")
        self.assertIsNone(val)
        self.assertIsNotNone(err)

    def test_validate_invalid_date(self):
        d, err = self.app._validate_date("31-01-2024")
        self.assertIsNone(d)
        self.assertIsNotNone(err)

    def test_filter_incorrect_date_order(self):
        self.app.date_start.delete(0, tk.END); self.app.date_start.insert(0, "2024-02-01")
        self.app.date_end.delete(0, tk.END); self.app.date_end.insert(0, "2024-01-01")
        # Приложение покажет messagebox, но тест проверяет, что логика не падает
        self.app.apply_filters()
        self.assertEqual(self.total_label.cget("text"), "0.00 ₽")

    # Граничные/Системные тесты
    def test_json_save_and_load(self):
        self.app.expenses = [{"amount": 99.99, "category": "Тест", "date": "2025-06-15"}]
        self.app.save_data()
        loaded = self.app.load_data()
        self.assertEqual(self.app.expenses, loaded)

    def test_empty_filter_returns_all(self):
        self.app.expenses = [{"amount": 10, "category": "Еда", "date": "2024-01-01"}]
        self.app.apply_filters()
        self.assertEqual(len(self.app.tree.get_children()), 1)

if __name__ == "__main__":
    unittest.main()
