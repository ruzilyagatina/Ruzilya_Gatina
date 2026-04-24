import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker")
        self.root.geometry("850x620")
        self.expenses = self.load_data()
        self._setup_ui()
        self._update_table()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    def load_data(self):
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return []

    def save_data(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.expenses, f, ensure_ascii=False, indent=2)

    def _setup_ui(self):
        # Ввод расходов
        input_frame = ttk.LabelFrame(self.root, text="Добавить расход", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.amount_entry = ttk.Entry(input_frame, width=15)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.category_combo = ttk.Combobox(input_frame, values=["Еда", "Транспорт", "Развлечения", "Жильё", "Здоровье", "Другое"], state="readonly", width=15)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.current(0)

        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=12)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        self.add_btn = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)

        # Фильтрация
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация и расчёт", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.filter_cat = ttk.Combobox(filter_frame, values=["Все", "Еда", "Транспорт", "Развлечения", "Жильё", "Здоровье", "Другое"], state="readonly", width=15)
        self.filter_cat.grid(row=0, column=1, padx=5, pady=5)
        self.filter_cat.current(0)

        ttk.Label(filter_frame, text="С:").grid(row=0, column=2, sticky="w", padx=5, pady=5)
        self.date_start = ttk.Entry(filter_frame, width=12)
        self.date_start.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(filter_frame, text="По:").grid(row=0, column=4, sticky="w", padx=5, pady=5)
        self.date_end = ttk.Entry(filter_frame, width=12)
        self.date_end.grid(row=0, column=5, padx=5, pady=5)

        self.filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filters)
        self.filter_btn.grid(row=0, column=6, padx=10, pady=5)

        # Таблица
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.tree = ttk.Treeview(table_frame, columns=("amount", "category", "date"), show="headings")
        self.tree.heading("amount", text="Сумма (₽)")
        self.tree.heading("category", text="Категория")
        self.tree.heading("date", text="Дата")
        self.tree.column("amount", width=120, anchor="center")
        self.tree.column("category", width=180, anchor="center")
        self.tree.column("date", width=130, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        # Итого
        total_frame = ttk.Frame(self.root)
        total_frame.pack(fill="x", padx=10, pady=10)
        ttk.Label(total_frame, text="Итого за период:").pack(side="left", padx=5)
        self.total_label = ttk.Label(total_frame, text="0.00 ₽", font=("Arial", 12, "bold"))
        self.total_label.pack(side="left", padx=5)

    def _validate_amount(self, val):
        try:
            amount = float(val.replace(",", "."))
            if amount <= 0:
                return None, "Сумма должна быть положительным числом."
            return round(amount, 2), None
        except ValueError:
            return None, "Некорректный формат суммы."

    def _validate_date(self, val):
        try:
            return datetime.strptime(val, "%Y-%m-%d").date(), None
        except ValueError:
            return None, "Неверный формат даты. Используйте ГГГГ-ММ-ДД."

    def add_expense(self):
        amount_str = self.amount_entry.get().strip()
        category = self.category_combo.get()
        date_str = self.date_entry.get().strip()

        amount, err = self._validate_amount(amount_str)
        if err:
            messagebox.showerror("Ошибка ввода", err)
            return

        date_obj, err = self._validate_date(date_str)
        if err:
            messagebox.showerror("Ошибка ввода", err)
            return

        self.expenses.append({"amount": amount, "category": category, "date": date_str})
        self.save_data()
        self._update_table()
        self.amount_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        messagebox.showinfo("Успех", "Расход успешно добавлен!")

    def apply_filters(self):
        cat = self.filter_cat.get()
        start_str = self.date_start.get().strip()
        end_str = self.date_end.get().strip()

        start_date, err1 = (None, None) if not start_str else self._validate_date(start_str)
        end_date, err2 = (None, None) if not end_str else self._validate_date(end_str)

        if err1: messagebox.showerror("Ошибка", err1); return
        if err2: messagebox.showerror("Ошибка", err2); return
        if start_date and end_date and start_date > end_date:
            messagebox.showerror("Ошибка", "Дата начала не может быть позже даты окончания."); return

        filtered = []
        for exp in self.expenses:
            d = datetime.strptime(exp["date"], "%Y-%m-%d").date()
            if cat != "Все" and exp["category"] != cat: continue
            if start_date and d < start_date: continue
            if end_date and d > end_date: continue
            filtered.append(exp)

        self._update_table(filtered)
        total = sum(e["amount"] for e in filtered)
        self.total_label.config(text=f"{total:.2f} ₽")

    def _update_table(self, data=None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        data = data if data is not None else self.expenses
        for exp in 
            self.tree.insert("", "end", values=(f"{exp['amount']:.2f}", exp["category"], exp["date"]))
        if data is None:
            self.total_label.config(text=f"{sum(e['amount'] for e in self.expenses):.2f} ₽")

    def _on_close(self):
        self.save_data()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()
