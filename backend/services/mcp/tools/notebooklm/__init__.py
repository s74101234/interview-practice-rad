from pathlib import Path
from typing import Callable

from . import agent


def run(file_path: str, title: str = "Interview Practice Notebook",
        log_fn: Callable[[str], None] | None = None) -> str:
    """同步執行，須透過 asyncio.to_thread 在執行緒中呼叫。"""

    def log(msg: str) -> None:
        if log_fn:
            log_fn(f"[Browser] {msg}")

    abs_path = str(Path(file_path).resolve())
    return agent.run(abs_path, title, log)
