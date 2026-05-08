# ops/sysmon.py
import time
import json
import psutil
import yaml
from rich.console import Console
from rich.table import Table
from ops.utils import load_config, save_json, timestamp


class SystemMonitor:
    def __init__(self, config_path=None):
        cfg = load_config().get("sysmon", {})
        self.interval = cfg.get("interval", 2)
        self.samples = cfg.get("samples", 5)
        self.output_file = cfg.get("output_file", "reports/sysmon_report.json")
        self.console = Console()
        self.data = []

        if config_path:
            try:
                # YAML gebruiken omdat dat makkelijker leesbaar is dan JSON voor configuratie
                with open(config_path, "r") as f:
                    user_cfg = yaml.safe_load(f)
                self.interval = user_cfg.get("interval", self.interval)
                self.samples = user_cfg.get("samples", self.samples)
            except Exception:
                pass

    def collect(self):
        print(f"[SYSMON] Collecting {self.samples} samples every {self.interval}s")

        for _ in range(self.samples):
            entry = {
                "timestamp": timestamp(),
                "cpu_percent": psutil.cpu_percent(interval=None),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_percent": psutil.disk_usage("/").percent,
                "net_sent": psutil.net_io_counters().bytes_sent,
                "net_recv": psutil.net_io_counters().bytes_recv
            }
            self.data.append(entry)
            time.sleep(self.interval)

        self._display()
        self._save()

    def _display(self):
        table = Table(title="System Monitor")
        table.add_column("Timestamp", style="cyan")
        table.add_column("CPU %", style="green")
        table.add_column("RAM %", style="yellow")
        table.add_column("Disk %", style="red")

        for entry in self.data:
            table.add_row(
                entry["timestamp"],
                str(entry["cpu_percent"]),
                str(entry["memory_percent"]),
                str(entry["disk_percent"])
            )

        self.console.print(table)

    def _save(self):
        report = {
            "timestamp": timestamp(),
            "samples": self.samples,
            "interval": self.interval,
            "data": self.data
        }
        save_json(report, self.output_file)
        print(f"[SYSMON] Report saved to {self.output_file}")


def run_sysmon(args):
    mon = SystemMonitor(config_path=args.config)
    mon.collect()

