import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ops.sysmon import SystemMonitor


class TestSystemMonitor(unittest.TestCase):
    def test_collect_runs(self):
        monitor = SystemMonitor()
        monitor.samples = 1
        monitor.interval = 0
        monitor.collect()
        self.assertTrue(len(monitor.data) >= 1)

    def test_data_has_cpu(self):
        monitor = SystemMonitor()
        monitor.samples = 1
        monitor.interval = 0
        monitor.collect()
        self.assertIn("cpu_percent", monitor.data[0])

    def test_data_has_memory(self):
        monitor = SystemMonitor()
        monitor.samples = 1
        monitor.interval = 0
        monitor.collect()
        self.assertIn("memory_percent", monitor.data[0])

    def test_report_saved(self):
        monitor = SystemMonitor()
        monitor.samples = 1
        monitor.interval = 0
        monitor.collect()
        self.assertTrue(os.path.exists("reports/sysmon_report.json"))


if __name__ == "__main__":
    unittest.main()
