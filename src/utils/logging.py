import logging
from functools import lru_cache

from rich.console import Console
from rich.logging import RichHandler
from rich.style import Style
from rich.theme import Theme

theme = Theme({
    "logging.level.info": "green",
    "logging.level.debug": "orange3"
})
base_style = Style(color="white")
console = Console(color_system="256", tab_size=4, width=120, style=base_style, theme=theme)


@lru_cache
def get_logger(module_name: str) -> logging.Logger:
    logger = logging.getLogger(module_name)
    handler = RichHandler(rich_tracebacks=True, console=console, tracebacks_show_locals=True, show_path=False)
    # handler.setFormatter(logging.Formatter("[ %(threadName)s:%(funcName)s:%(lineno)d ] - %(message)s"))
    handler.setFormatter(logging.Formatter(" %(message)s"))
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    return logger
