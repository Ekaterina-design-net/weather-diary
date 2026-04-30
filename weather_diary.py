import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

class WeatherDiary:
    def __init__(self, root):
        self.root = root
        self.root.title("Weather Diary - Дневник погоды")
        self.root.geometry("800x500")
        self.data_file = "weather_data.json"
        self.entries = self.load_data()

        # Поля ввода
        tk.Label(root, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.date_entry = tk.Entry(root, width=20)
        self.date_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(root, text="Температура (°C):").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.temp_entry = tk.Entry(root, width=20)
        self.temp_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(root, text="Описание погоды:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.desc_entry = tk.Entry(root, width=40)
        self.desc_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(root, text="Осадки:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.precip_var = tk.BooleanVar()
        tk.Checkbutton(root, text="Да", variable=self.precip_var).grid(row=3, column=1, sticky="w")

        # Кнопки
        tk.Button(root, text="Добавить запись", command=self.add_entry, bg="lightgreen").grid(row=4, column=0, pady=10)
        tk.Button(root, text="Сохранить в JSON", command=self.save_to_file, bg="lightblue").grid(row=4, column=1, pady=10)
        tk.Button(root, text="Загрузить из JSON", command=self.load_from_file, bg="lightyellow").grid(row=4, column=2, pady=10)

        # Фильтры
        filter_frame = tk.LabelFrame(root, text="Фильтрация", padx=5, pady=5)
        filter_frame.grid(row=5, column=0, columnspan=3, pady=10, sticky="ew", padx=5)

        tk.Label(filter_frame, text="Фильтр по дате (ГГГГ-ММ-ДД):").grid(row=0, column=0, padx=5)
        self.filter_date_entry = tk.Entry(filter_frame, width=15)
        self.filter_date_entry.grid(row=0, column=1, padx=5)
        tk.Button(filter_frame, text="Применить", command=self.filter_by_date).grid(row=0, column=2, padx=5)

        tk.Label(filter_frame, text="Фильтр по температуре (> °C):").grid(row=1, column=0, padx=5)
        self.filter_temp_entry = tk.Entry(filter_frame, width=10)
        self.filter_temp_entry.grid(row=1, column=1, padx=5)
        tk.Button(filter_frame, text="Применить", command=self.filter_by_temp).grid(row=1, column=2, padx=5)

        tk.Button(filter_frame, text="Сбросить фильтр", command=self.refresh_table, bg="lightgray").grid(row=2, column=0, columnspan=3, pady=5)

        # Таблица
        self.tree = ttk.Treeview(root, columns=("date", "temp", "desc", "precip"), show="headings")
        self.tree.heading("date", text="Дата")
        self.tree.heading("temp", text="Температура (°C)")
        self.tree.heading("desc", text="Описание")
        self.tree.heading("precip", text="Осадки")
        self.tree.column("date", width=120)
        self.tree.column("temp", width=80)
        self.tree.column("desc", width=250)
        self.tree.column("precip", width=80)
        self.tree.grid(row=6, column=0, columnspan=3, pady=10, padx=5, sticky="nsew")

        scrollbar = ttk.Scrollbar(root, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=6, column=3, sticky="ns")
        self.tree.configure(yscrollcommand=scrollbar.set)

        root.grid_rowconfigure(6, weight=1)
        root.grid_columnconfigure(0, weight=1)

        self.refresh_table()

    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    def add_entry(self):
        date = self.date_entry.get().strip()
        temp = self.temp_entry.get().strip()
        desc = self.desc_entry.get().strip()
        precip = self.precip_var.get()

        if not date:
            messagebox.showerror("Ошибка", "Дата не может быть пустой")
            return
        if not self.validate_date(date):
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД")
            return
        if not temp:
            messagebox.showerror("Ошибка", "Температура не может быть пустой")
            return
        try:
            temp_float = float(temp)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return
        if not desc:
            messagebox.showerror("Ошибка", "Описание не может быть пустым")
            return

        self.entries.append({
            "date": date,
            "temperature": temp_float,
            "description": desc,
            "precipitation": precip
        })
        self.refresh_table()
        self.clear_inputs()
        messagebox.showinfo("Успех", "Запись добавлена")

    def clear_inputs(self):
        self.date_entry.delete(0, tk.END)
        self.temp_entry.delete(0, tk.END)
        self.desc_entry.delete(0, tk.END)
        self.precip_var.set(False)

    def refresh_table(self, filtered_entries=None):
        for row in self.tree.get_children():
            self.tree.delete(row)

        display_data = filtered_entries if filtered_entries is not None else self.entries
        for entry in display_data:
            precip_text = "Да" if entry["precipitation"] else "Нет"
            self.tree.insert("", tk.END, values=(
                entry["date"],
                entry["temperature"],
                entry["description"],
                precip_text
            ))

    def filter_by_date(self):
        filter_date = self.filter_date_entry.get().strip()
        if not filter_date:
            messagebox.showwarning("Предупреждение", "Введите дату для фильтрации")
            return
        if not self.validate_date(filter_date):
            messagebox.showerror("Ошибка", "Неверный формат даты")
            return

        filtered = [e for e in self.entries if e["date"] == filter_date]
        self.refresh_table(filtered)
        messagebox.showinfo("Результат", f"Найдено {len(filtered)} записей")

    def filter_by_temp(self):
        filter_temp = self.filter_temp_entry.get().strip()
        if not filter_temp:
            messagebox.showwarning("Предупреждение", "Введите температуру для фильтрации")
            return
        try:
            temp_threshold = float(filter_temp)
        except ValueError:
            messagebox.showerror("Ошибка", "Температура должна быть числом")
            return

        filtered = [e for e in self.entries if e["temperature"] > temp_threshold]
        self.refresh_table(filtered)
        messagebox.showinfo("Результат", f"Найдено {len(filtered)} записей с температурой > {temp_threshold}°C")

    def save_to_file(self):
        try:
            with open(self.data_file, "w", encoding="utf-8") as f:
                json.dump(self.entries, f, ensure_ascii=False, indent=4)
            messagebox.showinfo("Успех", f"Данные сохранены в {self.data_file}")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить: {e}")

    def load_from_file(self):
        if not os.path.exists(self.data_file):
            messagebox.showwarning("Предупреждение", f"Файл {self.data_file} не найден")
            return
        try:
            with open(self.data_file, "r", encoding="utf-8") as f:
                self.entries = json.load(f)
            self.refresh_table()
            messagebox.showinfo("Успех", f"Загружено {len(self.entries)} записей")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось загрузить: {e}")

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

if __name__ == "__main__":
    root = tk.Tk()
    app = WeatherDiary(root)
    root.mainloop()
