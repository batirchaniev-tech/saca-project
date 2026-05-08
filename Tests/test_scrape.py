import sys
import os
import json
import unittest
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ops.scrape import WebScraper

DUMMY_HTML = """
<html>
<head><title>Test Page</title></head>
<body>
<p>Hello world</p>
<p>Contact us at test@example.com or info@test.org</p>
<a href="https://example.com">Link 1</a>
<a href="https://test.org">Link 2</a>
</body>
</html>
"""


class TestWebScraper(unittest.TestCase):
    def _make_mock_response(self):
        mock_resp = MagicMock()
        mock_resp.text = DUMMY_HTML
        mock_resp.status_code = 200
        mock_resp.raise_for_status = MagicMock()
        return mock_resp

    @patch("ops.scrape.requests.get")
    def test_elements_extracted(self, mock_get):
        mock_get.return_value = self._make_mock_response()
        scraper = WebScraper("http://test.local", selector="p")
        results = scraper.scrape()
        self.assertIn("Hello world", results)

    @patch("ops.scrape.requests.get")
    def test_emails_detected(self, mock_get):
        mock_get.return_value = self._make_mock_response()
        scraper = WebScraper("http://test.local", selector="p")
        scraper.scrape()
        self.assertIn("test@example.com", scraper.emails)

    @patch("ops.scrape.requests.get")
    def test_emails_include_both(self, mock_get):
        mock_get.return_value = self._make_mock_response()
        scraper = WebScraper("http://test.local", selector="p")
        scraper.scrape()
        self.assertIn("info@test.org", scraper.emails)

    @patch("ops.scrape.requests.get")
    def test_css_selector_works(self, mock_get):
        mock_get.return_value = self._make_mock_response()
        scraper = WebScraper("http://test.local", selector="p")
        results = scraper.scrape()
        self.assertTrue(len(results) >= 1)

    @patch("ops.scrape.requests.get")
    def test_report_saved(self, mock_get):
        mock_get.return_value = self._make_mock_response()
        scraper = WebScraper("http://test.local")
        scraper.scrape()
        self.assertTrue(os.path.exists("reports/scrape_report.json"))


if __name__ == "__main__":
    unittest.main()
