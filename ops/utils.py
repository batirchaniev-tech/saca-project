# ops/utils.py
import sys
import json
import os
import datetime
from pathlib import Path
import base64


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_json(data, path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, default=str)

def load_config():
    cfg = Path(__file__).parent.parent / "data" / "config.json"
    return load_json(cfg)

def load_iocs():
    iocs = Path(__file__).parent.parent / "data" / "iocs.json"
    return load_json(iocs)

def timestamp():
    return datetime.datetime.now().isoformat()

def ensure_dir(path):
    Path(path).mkdir(parents=True, exist_ok=True)

def b64_encode(text):
    return base64.b64encode(text.encode()).decode()

def b64_decode(text):
    return base64.b64decode(text.encode()).decode()

# Toolkit stopt meteen als de Python versie te oud is om te werken
def check_python_version(min_major=3, min_minor=10):
    if sys.version_info < (min_major, min_minor):
        print(f"[!] Python {min_major}.{min_minor}+ required. Current: {sys.version}")
        sys.exit(1)

