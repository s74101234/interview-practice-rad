from . import search_knowledge
from backend.core.config import settings

notebooklm = None
if settings.notebooklm_enabled:
    try:
        from . import notebooklm as _notebooklm
        notebooklm = _notebooklm
    except Exception:
        pass

__all__ = ["search_knowledge", "notebooklm"]
