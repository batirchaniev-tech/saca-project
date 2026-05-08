import sys
import os
import json
import unittest
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ops.files import FileScanner


class TestFileScanner(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        clean_file = os.path.join(self.tmpdir, "readme.txt")
        with open(clean_file, "w") as f:
            f.write("This is a normal file.")

        sus_file = os.path.join(self.tmpdir, "backdoor.bat")
        with open(sus_file, "w") as f:
            f.write("cmd.exe /c whoami")

        pattern_file = os.path.join(self.tmpdir, "script.py")
        with open(pattern_file, "w") as f:
            f.write("password = 'secret123'")

    def test_detects_suspicious_extension(self):
        scanner = FileScanner(self.tmpdir)
        results = scanner.scan()
        sus = [r for r in results if r["suspicious"]]
        extensions = [r["extension"] for r in sus]
        self.assertIn(".bat", extensions)

    def test_detects_suspicious_keyword_in_name(self):
        scanner = FileScanner(self.tmpdir)
        results = scanner.scan()
        sus = [r for r in results if r["suspicious"]]
        filenames = [os.path.basename(r["file"]) for r in sus]
        self.assertIn("backdoor.bat", filenames)

    def test_detects_pattern_in_content(self):
        scanner = FileScanner(self.tmpdir)
        results = scanner.scan()
        sus = [r for r in results if r["suspicious"]]
        filenames = [os.path.basename(r["file"]) for r in sus]
        self.assertIn("script.py", filenames)

    def test_clean_file_not_flagged(self):
        scanner = FileScanner(self.tmpdir)
        results = scanner.scan()
        clean = [r for r in results if not r["suspicious"]]
        filenames = [os.path.basename(r["file"]) for r in clean]
        self.assertIn("readme.txt", filenames)

    def test_report_saved(self):
        scanner = FileScanner(self.tmpdir)
        scanner.scan()
        self.assertTrue(os.path.exists("reports/scan_report.json"))


if __name__ == "__main__":
    unittest.main()
