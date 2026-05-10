import json
from pathlib import Path

_SCHEMAS = Path(__file__).resolve().parent.parent.parent / "mcp" / "tools"


def load_tools() -> list[dict]:
    """載入 mcp/tools/ 下所有 JSON 工具定義。"""
    tools: list[dict] = []
    for path in sorted(_SCHEMAS.glob("*.json")):
        tools.extend(json.loads(path.read_text(encoding="utf-8")))
    return tools
