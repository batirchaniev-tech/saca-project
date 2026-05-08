# ops/files.py
import os
import re
import glob
import shutil
import fnmatch
from pathlib import Path
from ops.utils import load_iocs, load_config, save_json, timestamp

try:
    import send2trash
    HAS_SEND2TRASH = True
except ImportError:
    HAS_SEND2TRASH = False


class FileScanner:
    def __init__(self, directory, quarantine=False):
        self.directory = Path(directory)
        self.quarantine = quarantine
        self.iocs = load_iocs()
        self.config = load_config().get("scan", {})
        self.results = []

        self.suspicious_ext = self.iocs.get("suspicious_extensions", [".exe", ".bat", ".ps1"])
        self.suspicious_names = self.iocs.get("suspicious_filenames", ["hack", "crack", "keygen"])
        self.patterns = self.iocs.get("suspicious_patterns", [r"password\s*=", r"api[_-]?key"])

    def _match_patterns(self, filepath):
        hits = []
        try:
            with open(filepath, "r", errors="ignore") as f:
                content = f.read()
            for pat in self.patterns:
                if re.search(pat, content, re.IGNORECASE):
                    hits.append(pat)
        except Exception:
            pass
        return hits

    def _check_name(self, name):
        low = name.lower()
        for kw in self.suspicious_names:
            if kw.lower() in low:
                return True
        patterns = self.iocs.get("suspicious_filename_patterns", ["*.exe", "*.bat", "crack_*", "hack_*"])
        for pat in patterns:
            if fnmatch.fnmatch(low, pat):
                return True
        return False

#send2trash gooit het bestand naar de prullenbak, shutil verplaatst het als send2trash niet geïnstalleerd is
    def _quarantine(self, path):
        qdir = Path(self.config.get("quarantine_dir", "quarantine"))
        qdir.mkdir(parents=True, exist_ok=True)
        dest = qdir / path.name
        if HAS_SEND2TRASH:
            send2trash.send2trash(str(path))
            return "trash"
        shutil.move(str(path), str(dest))
        return str(dest)

    def scan(self):
        base = str(self.directory)
        # ** zorgt dat hij ook in submappen zoekt, niet alleen de hoofdmap
        files = glob.glob(os.path.join(base, "**"), recursive=True)
        files = [Path(f) for f in files if Path(f).is_file()]

        for f in files:
            info = {
                "file": str(f),
                "extension": f.suffix.lower(),
                "size": f.stat().st_size,
                "suspicious": False,
                "reasons": [],
                "timestamp": timestamp(),
                "quarantined": False,
                "quarantine_dest": None,
            }

            if info["extension"] in self.suspicious_ext:
                info["suspicious"] = True
                info["reasons"].append(f"suspicious extension {info['extension']}")

            if self._check_name(f.name):
                info["suspicious"] = True
                info["reasons"].append("suspicious filename keyword")

            pats = self._match_patterns(f)
            for p in pats:
                info["suspicious"] = True
                info["reasons"].append(f"pattern match: {p}")

            if info["suspicious"] and self.quarantine:
                dest = self._quarantine(f)
                info["quarantined"] = True
                info["quarantine_dest"] = dest

            self.results.append(info)

        self._save_report()
        return self.results

    def _save_report(self):
        report = {
            "directory": str(self.directory),
            "total_files": len(self.results),
            "suspicious": sum(1 for r in self.results if r["suspicious"]),
            "timestamp": timestamp(),
            "findings": self.results,
        }
        out = self.config.get("log_file", "reports/scan_report.json")
        save_json(report, out)

    def print_summary(self):
        print(f"[SCAN] Directory: {self.directory}")
        print(f"[SCAN] Total files: {len(self.results)}")
        sus = [r for r in self.results if r["suspicious"]]
        print(f"[SCAN] Suspicious: {len(sus)}")
        for r in sus:
            print(f"  [!] {r['file']}")
            for reason in r["reasons"]:
                print(f"      - {reason}")


def run_scan(args):
    scanner = FileScanner(args.path, quarantine=args.quarantine)
    scanner.scan()
    scanner.print_summary()


