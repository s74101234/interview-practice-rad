import os
from . import search_knowledge

# NotebookLM 需要本地 Windows + Edge 瀏覽器，雲端部署時停用
notebooklm = None
if os.getenv("NOTEBOOKLM_ENABLED", "true").lower() == "true":
    try:
        from . import notebooklm as _notebooklm
        notebooklm = _notebooklm
    except Exception:
        pass

__all__ = ["search_knowledge", "notebooklm"]
