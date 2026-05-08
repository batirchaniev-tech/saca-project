# ops/net.py
import socket
import threading
import random
import time
import itertools
import ipaddress
from ops.utils import load_config, save_json, timestamp


class NetworkScanner:
    def __init__(self, target, ports=None, threads=50, timeout=1.0):
        self.target = target
        self.timeout = timeout
        self.thread_count = max(1, threads)
        self.open_ports = []
        self.lock = threading.Lock()

        self.cfg = load_config().get("net_scan", {})
        if ports:
            self.ports = [p for p in ports if isinstance(p, int) and 1 <= p <= 65535]
        else:
            self.ports = self.cfg.get("common_ports", [22, 80, 443, 3389])

    def _resolve_targets(self):
        targets = []
        try:
            net = ipaddress.ip_network(self.target, strict=False)
            for ip in net.hosts():
                targets.append(str(ip))
        except ValueError:
            targets.append(self.target)
        return targets

    def _scan_port(self, host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(self.timeout)
                res = s.connect_ex((host, port))
                if res == 0:
                    try:
                        service = socket.getservbyport(port)
                    except OSError:
                        service = "unknown"

                    with self.lock:
                        self.open_ports.append({
                            "host": host,
                            "port": port,
                            "service": service,
                            "timestamp": timestamp()
                        })
                        print(f"  [OPEN] {host}:{port} ({service})")
        except Exception:
            pass

    def _worker(self, tasks):
        for host, port in tasks:
            self._scan_port(host, port)
            time.sleep(random.uniform(0.0, 0.03))

    def scan(self):
        targets = self._resolve_targets()
        combos = list(itertools.product(targets, self.ports))
        # Willekeurige volgorde zodat een firewall of IDS het niet herkent als portscan
        random.shuffle(combos)

        print(f"[NET-SCAN] Hosts: {len(targets)}, Ports per host: {len(self.ports)}")

        if not combos:
            return []
        # Voorkomt deling door nul als er meer threads zijn dan combinaties
        chunk_size = max(1, len(combos) // self.thread_count)
        chunks = [combos[i:i + chunk_size] for i in range(0, len(combos), chunk_size)]

        threads = []
        for ch in chunks:
            t = threading.Thread(target=self._worker, args=(ch,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

        self._save_report()
        return self.open_ports

    def _save_report(self):
        report = {
            "target": self.target,
            "open_ports": self.open_ports,
            "total_open": len(self.open_ports),
            "timestamp": timestamp()
        }
        out = self.cfg.get("log_file", "reports/netscan_report.json")
        save_json(report, out)

    def print_summary(self):
        print(f"\n[NET-SCAN] Open ports: {len(self.open_ports)}")
        for e in self.open_ports:
            print(f"  {e['host']}:{e['port']} -> {e['service']}")


def run_net_scan(args):
    ports = None
    if args.ports:
        parts = [p.strip() for p in args.ports.split(",")]
        ports = []
        for p in parts:
            if p.isdigit():
                n = int(p)
                if 1 <= n <= 65535:
                    ports.append(n)

    scanner = NetworkScanner(
        target=args.target,
        ports=ports,
        threads=args.threads,
        timeout=args.timeout
    )
    scanner.scan()
    scanner.print_summary()

