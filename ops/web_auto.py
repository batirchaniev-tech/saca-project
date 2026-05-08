# ops/web_auto.py
import base64
import datetime
from pathlib import Path
from ops.utils import load_config, ensure_dir

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    HAS_SELENIUM = True
except ImportError:
    HAS_SELENIUM = False

try:
    import image_viewer
    HAS_IMAGE_VIEWER = True
except ImportError:
    HAS_IMAGE_VIEWER = False


class WebAutomationBot:
    def __init__(self, url, headless=True):
        self.url = url
        self.headless = headless
        cfg = load_config().get("web_auto", {})
        self.screenshot_dir = Path(cfg.get("screenshot_dir", "screenshots"))
        ensure_dir(self.screenshot_dir)
        self.driver = None

    def _setup_driver(self):
        options = Options()
        if self.headless:
            options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        self.driver = webdriver.Chrome(options=options)

    def run(self):
        if not HAS_SELENIUM:
            print("[!] Selenium not installed. Run: pip install selenium")
            return

        print(f"[WEB-AUTO] Opening: {self.url}")

        try:
            self._setup_driver()
            self.driver.get(self.url)

            title = self.driver.title
            print(f"[WEB-AUTO] Page title: {title}")

            name = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.screenshot_dir / f"screenshot_{name}.png"

            self.driver.save_screenshot(str(screenshot_path))
            print(f"[WEB-AUTO] Screenshot saved: {screenshot_path}")

            with open(screenshot_path, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
            print(f"[WEB-AUTO] Base64 length: {len(b64)}")

            if HAS_IMAGE_VIEWER:
                image_viewer.show(str(screenshot_path))
            else:
                print(f"[WEB-AUTO] image_viewer not installed.")

        except Exception as e:
            print(f"[!] Web automation error: {e}")

        finally:
            if self.driver:
                self.driver.quit()


def run_web_auto(args):
    bot = WebAutomationBot(
        url=args.url,
        headless=not args.no_headless
    )
    bot.run()

