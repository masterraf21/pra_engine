import logging
from functools import lru_cache

from rich.console import Console
from rich.logging import RichHandler
from rich.style import Style

base_style = Style(color="magenta")
console = Console(color_system="256", width=150, style=base_style)


@lru_cache
def get_logger(module_name: str) -> logging.Logger:
    logger = logging.getLogger(module_name)
    handler = RichHandler(rich_tracebacks=True, console=console, tracebacks_show_locals=True)
    # handler.setFormatter(logging.Formatter("[ %(threadName)s:%(funcName)s:%(lineno)d ] - %(message)s"))
    handler.setFormatter(logging.Formatter("%(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger
