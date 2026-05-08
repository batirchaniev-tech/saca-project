# main.py
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from ops.utils import check_python_version
from ops.cli import main

check_python_version()

if __name__ == "__main__":
    main()