import unittest
import json
import os
import tempfile
import tkinter as tk
from weather_diary import WeatherDiary

class TestWeatherDiary(unittest.TestCase):
    def setUp(self):
        self.root = tk.Tk()
        self.app = WeatherDiary(self.root)
        self.test_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
        self.app.data_file = self.test_file.name

    def tearDown(self):
        self.root.destroy()
        if os.path.exists(self.test_file.name):
            os.unlink(self.test_file.name)

    def test_validate_date_correct(self):
        self.assertTrue(self.app.validate_date("2024-12-31"))
        self.assertTrue(self.app.validate_date("2025-01-01"))

    def test_validate_date_incorrect(self):
        self.assertFalse(self.app.validate_date("31-12-2024"))
        self.assertFalse(self.app.validate_date("2024-13-01"))

    def test_add_entry_valid(self):
        self.app.date_entry.insert(0, "2024-06-15")
        self.app.temp_entry.insert(0, "22.5")
        self.app.desc_entry.insert(0, "Солнечно")
        self.app.precip_var.set(False)
        self.app.add_entry()
        self.assertEqual(len(self.app.entries), 1)
        self.assertEqual(self.app.entries[0]["temperature"], 22.5)

    def test_add_entry_empty_date(self):
        self.app.add_entry()
        self.assertEqual(len(self.app.entries), 0)

    def test_save_and_load_json(self):
        self.app.entries = [{"date": "2024-06-15", "temperature": 22.5, "description": "Тест", "precipitation": False}]
        self.app.save_to_file()
        self.app.entries = []
        self.app.load_from_file()
        self.assertEqual(len(self.app.entries), 1)

if __name__ == "__main__":
    unittest.main()
