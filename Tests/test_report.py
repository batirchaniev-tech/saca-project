import sys
import os
import json
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ops.report import ReportManager


class TestReportManager(unittest.TestCase):
    def setUp(self):
        os.makedirs("reports", exist_ok=True)
        with open("reports/test_a.json", "w") as f:
            json.dump({"source": "a", "data": 1}, f)
        with open("reports/test_b.json", "w") as f:
            json.dump({"source": "b", "data": 2}, f)

    def test_reports_found(self):
        mgr = ReportManager()
        reports = mgr.list_reports()
        names = [r.name for r in reports]
        self.assertIn("test_a.json", names)

    def test_merged_report_saved(self):
        mgr = ReportManager()
        mgr.merge_reports()
        self.assertTrue(os.path.exists("reports/merged_report.json"))

    def test_load_report(self):
        mgr = ReportManager()
        data = mgr.load_report("reports/test_a.json")
        self.assertEqual(data["source"], "a")

    def test_load_invalid_report(self):
        mgr = ReportManager()
        data = mgr.load_report("reports/nonexistent.json")
        self.assertIsNone(data)


if __name__ == "__main__":
    unittest.main()
