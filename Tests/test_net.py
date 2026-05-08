import sys
import os
import socket
import threading
import unittest
import time


sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ops.net import NetworkScanner


def start_dummy_server(port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(("127.0.0.1", port))
    server.listen(1)
    server.settimeout(3)
    try:
        conn, _ = server.accept()
        conn.close()
    except Exception:
        pass
    finally:
        server.close()


class TestNetworkScanner(unittest.TestCase):
    def test_open_port_detected(self):
        port = 19876
        t = threading.Thread(target=start_dummy_server, args=(port,))
        t.daemon = True
        t.start()


        time.sleep(0.2)

        scanner = NetworkScanner("127.0.0.1", ports=[port], timeout=2)
        scanner.scan()
        open_ports = [e["port"] for e in scanner.open_ports]
        self.assertIn(port, open_ports)

    def test_closed_port_not_detected(self):
        scanner = NetworkScanner("127.0.0.1", ports=[19877], timeout=0.5)
        scanner.scan()
        self.assertEqual(len(scanner.open_ports), 0)

    def test_cidr_expands_hosts(self):
        scanner = NetworkScanner("127.0.0.1/32", ports=[19878], timeout=0.3)
        targets = scanner._resolve_targets()
        self.assertEqual(targets, ["127.0.0.1"])


if __name__ == "__main__":
    unittest.main()
