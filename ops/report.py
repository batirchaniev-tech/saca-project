# ops/report.py
import json
import glob
import base64
import socket
import email.mime.text
import email.mime.multipart
from pathlib import Path
from ops.utils import load_config, timestamp

class ReportManager:
    def __init__(self):
        cfg = load_config().get("report", {})
        self.output_dir = Path(cfg.get("output_dir", "reports"))
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def load_report(self, path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None

    def list_reports(self):
        return list(self.output_dir.glob("*.json"))

    def merge_reports(self):
        merged = {
            "timestamp": timestamp(),
            "reports": []
        }
        for rep in self.list_reports():
            data = self.load_report(rep)
            if data:
                merged["reports"].append({
                    "file": rep.name,
                    "content": data
                })
        out = self.output_dir / "merged_report.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(merged, f, indent=2)
        print(f"[REPORT] Merged report saved to: {out}")

    def print_summary(self):
        reps = self.list_reports()
        print(f"[REPORT] Found {len(reps)} report files")
        for r in reps:
            print(f"  - {r.name}")

    def send_email(self, to_addr, subject, body):
        msg = email.mime.multipart.MIMEMultipart()
        msg["From"] = "toolkit@cybersec.local"
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg.attach(email.mime.text.MIMEText(body, "plain"))
        raw = msg.as_string()
        encoded = base64.b64encode(raw.encode()).decode()
        print(f"[REPORT] Email prepared, base64 preview: {encoded[:60]}...")
        cfg = load_config().get("report", {})
        host = cfg.get("smtp_host", "smtp.example.com")
        port = cfg.get("smtp_port", 25)
        try:
            with socket.create_connection((host, port), timeout=5) as sock:
                sock.sendall(b"QUIT\r\n")
                print("[REPORT] SMTP connection ok")
        except Exception as e:
            print(f"[REPORT] SMTP failed (expected in test): {e}")


def run_report(args):
    mgr = ReportManager()
    mgr.print_summary()
    mgr.merge_reports()
    if args.email:
        body = f"Merged report generated at {timestamp()}"
        mgr.send_email(args.email, "CyberSec Toolkit Report", body)