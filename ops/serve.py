# ops/serve.py
import json
import glob
import os
import http.server
from ops.utils import load_config, timestamp


class DashboardHandler(http.server.BaseHTTPRequestHandler):
    report_dir = "reports"

    def log_message(self, format, *args):
        print(f"[SERVE] {timestamp()} - {format % args}")

    # Alle JSON rapporten dynamisch inladen, geen vaste bestandsnamen nodig
    def _load_reports(self):
        reports = {}
        for path in glob.glob(os.path.join(self.report_dir, "*.json")):
            name = os.path.basename(path)
            try:
                with open(path) as f:
                    reports[name] = json.load(f)
            except Exception:
                reports[name] = {"error": "could not parse"}
        return reports

    def do_GET(self):
        if self.path == "/" or self.path == "/reports":
            data = self._load_reports()
            body = json.dumps(data, indent=2, default=str).encode()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", len(body))
            self.end_headers()
            self.wfile.write(body)
        elif self.path == "/health":
            body = b'{"status": "ok"}'
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "not found"}')


class Dashboard:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def start(self):
        server = http.server.HTTPServer((self.host, self.port), DashboardHandler)
        print(f"[SERVE] Dashboard running at http://{self.host}:{self.port}/reports")
        print("[SERVE] Press Ctrl+C to stop.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\n[SERVE] Stopped.")
            server.server_close()


def run_serve(args):
    dashboard = Dashboard(host=args.host, port=args.port)
    dashboard.start()

