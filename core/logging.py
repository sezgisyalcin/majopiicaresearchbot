
"""
Compatibility shim: some modules import `from core.logging import log`.
This file ensures that import works in all deployments.
"""
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def log(name: str = "bottany"):
    return logging.getLogger(name)
