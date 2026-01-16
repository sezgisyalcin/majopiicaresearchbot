
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

def log(name: str = "bottany"):
    return logging.getLogger(name)
