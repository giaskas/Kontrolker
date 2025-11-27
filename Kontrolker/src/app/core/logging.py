# src/app/core/logging.py
import logging
import sys

def setup_logging(level: int = logging.INFO) -> None:
    fmt = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(fmt))
    root = logging.getLogger()
    root.setLevel(level)
    # evita handlers duplicados en reload
    if not root.handlers:
        root.addHandler(handler)
        