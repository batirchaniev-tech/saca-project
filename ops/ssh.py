# ops/ssh.py
import json
import datetime
import subprocess
from ops.utils import load_config, save_json, timestamp

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False


class SSHClient:
    def __init__(self, host, username, password=None, key_path=None, port=22):
        self.host = host
        self.username = username
        self.password = password
        self.key_path = key_path
        self.port = port
        self.client = None
        self.results = []

        cfg = load_config().get("ssh", {})
        self.output_file = cfg.get("output_file", "reports/ssh_report.json")

    def connect(self):
        if not HAS_PARAMIKO:
            print("[!] Paramiko not installed. Run: pip install paramiko")
            return False

        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            if self.key_path:
                self.client.connect(
                    self.host,
                    port=self.port,
                    username=self.username,
                    key_filename=self.key_path,
                    timeout=5
                )
            else:
                self.client.connect(
                    self.host,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=5
                )

            print(f"[SSH] Connected to {self.host}:{self.port}")
            return True

        except Exception as e:
            print(f"[!] SSH connection failed: {e}")
            return False

    def execute(self, command):
        if not self.client:
            print("[!] Not connected.")
            return None

        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=5)
            out = stdout.read().decode(errors="ignore").strip()
            err = stderr.read().decode(errors="ignore").strip()

            entry = {
                "command": command,
                "stdout": out,
                "stderr": err,
                "timestamp": timestamp()
            }

            self.results.append(entry)

            print(f"[SSH] > {command}")
            if out:
                print(f"       {out}")
            if err:
                print(f"       ERR: {err}")

            return entry

        except Exception as e:
            print(f"[!] Command failed: {e}")
            return None

    def disconnect(self):
        if self.client:
            self.client.close()
            print("[SSH] Disconnected.")

    def save_report(self):
        report = {
            "host": self.host,
            "username": self.username,
            "timestamp": timestamp(),
            "saved_at": datetime.datetime.now().isoformat(),
            "commands": self.results
        }
        save_json(report, self.output_file)


class LocalRunner:
    @staticmethod
    def run(command):
        print(f"[LOCAL] Running: {command}")
        try:
            result = subprocess.run(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )
            output = result.stdout.decode(errors="ignore") or result.stderr.decode(errors="ignore") or "[No output]"
            print(output)
            log = json.dumps({"command": command, "output": output})
            return log
        except Exception as e:
            print(f"[LOCAL] Error: {e}")
            return None


def run_ssh(args):
    if args.local:
        LocalRunner.run(args.command)
        return

    client = SSHClient(
        host=args.host,
        username=args.username,
        password=args.password,
        key_path=args.key,
        port=args.port
    )

    if client.connect():
        # Meerdere commando's scheiden met ; zodat de gebruiker ze kan chainen
        for cmd in args.command.split(";"):
            client.execute(cmd.strip())
        client.save_report()
        client.disconnect()

