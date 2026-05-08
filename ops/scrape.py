# ops/scrape.py
import re
import datetime
import requests
from bs4 import BeautifulSoup
from ops.utils import load_config, save_json, timestamp

class WebScraper:
    def __init__(self, url, selector="p"):
        self.url = url
        self.selector = selector
        cfg = load_config().get("scrape", {})
        self.output_file = cfg.get("output_file", "reports/scrape_report.json")
        self.results = []
        self.emails = []
        self.email_pattern = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

    def scrape(self):
        try:
            r = requests.get(self.url, timeout=5)
        except Exception as e:
            print(f"[SCRAPE] Request error: {e}")
            return []

        if r.status_code != 200:
            print(f"[SCRAPE] HTTP {r.status_code}")
            return []

        soup = BeautifulSoup(r.text, "html.parser")
        elements = soup.select(self.selector)

        for el in elements:
            text = el.get_text(strip=True)
            if text:
                self.results.append(text)

        self.emails = list(set(self.email_pattern.findall(r.text)))

        self._save_report()
        return self.results

    def _save_report(self):
        report = {
            "url": self.url,
            "selector": self.selector,
            "timestamp": timestamp(),
            "scraped_at": datetime.datetime.now().isoformat(),
            "results": self.results,
            "emails_found": self.emails
        }
        save_json(report, self.output_file)

    def print_summary(self):
        print(f"[SCRAPE] URL: {self.url}")
        print(f"[SCRAPE] Selector: {self.selector}")
        print(f"[SCRAPE] Found: {len(self.results)} elements")
        print(f"[SCRAPE] Emails found: {self.emails}")
        for t in self.results[:10]:
            print(f"  - {t}")


def run_scrape(args):
    scraper = WebScraper(args.url, selector=args.selector)
    scraper.scrape()
    scraper.print_summary()

