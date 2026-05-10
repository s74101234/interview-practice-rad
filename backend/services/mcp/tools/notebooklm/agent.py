"""
Browser Automation Agent — 自包含的 Gemini ReAct 迴圈
不依賴 services/chat/ 或 services/models/，自己管理 Gemini 客戶端與 JSON 解析。
"""
import json
import subprocess
from pathlib import Path
from typing import Callable

from playwright.sync_api import sync_playwright

from core.config import settings
import core.app_state as state
from services.models.gemini import generate_text, MODEL
from . import browser

NOTEBOOKLM_URL = "https://notebooklm.google.com"
MAX_STEPS      = 20
_PROMPT_FILE   = Path(__file__).parent / "prompt_browser.md"
_BROWSER_JSON  = Path(__file__).parent / "browser.json"


def _load_tools() -> list[dict]:
    return json.loads(_BROWSER_JSON.read_text(encoding="utf-8"))


def _build_tools_context(tools: list[dict]) -> str:
    blocks = []
    for entry in tools:
        fn = entry.get("function", entry)
        name = fn["name"]
        desc = fn["description"]
        props = fn.get("parameters", {}).get("properties", {})
        required = fn.get("parameters", {}).get("required", [])
        lines = [f"## {name}", desc]
        for k, v in props.items():
            req = "必填" if k in required else "選填"
            lines.append(f"  - {k} ({v['type']}, {req})：{v['description']}")
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks)


def _build_system_prompt() -> str:
    template = _PROMPT_FILE.read_text(encoding="utf-8").strip()
    tools_context = _build_tools_context(_load_tools())
    return template.replace("{tools_context}", tools_context)


_SYSTEM = _build_system_prompt()


def _generate(messages: list[dict]) -> str:
    return generate_text(messages, _SYSTEM)


def _parse_json(raw: str) -> dict | None:
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        return None
    try:
        return json.loads(raw[start:end+1])
    except json.JSONDecodeError:
        return None


def run(file_path: str, title: str, log: Callable[[str], None]) -> str:
    _kill_edge()
    log("啟動 Edge 瀏覽器...")

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=settings.edge_user_data,
            channel="msedge",
            headless=False,
            args=[f"--profile-directory={settings.edge_profile}"],
        )
        context.grant_permissions(["clipboard-read", "clipboard-write"])
        page = context.new_page()
        page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded", timeout=30000)
        page.wait_for_timeout(2000)

        history: list[dict] = []
        last_result = "Agent 啟動，目前在 NotebookLM 首頁"

        for step in range(MAX_STEPS):
            if state.cancel_event.is_set():
                log("任務已取消")
                context.close()
                raise InterruptedError("任務已取消")

            page_state = browser.get_page_state(page)
            log(f"DOM：{page_state}")

            user_prompt = (
                f"PDF 路徑：{file_path}\n\n"
                f"上一步結果：{last_result}\n\n"
                f"目前頁面狀態：\n{page_state}\n\n"
                f"請決定下一步動作，輸出 JSON。"
            )

            messages = [*history, {"role": "user", "content": user_prompt}]
            log(f"第 {step+1} 步，推理中...")

            raw  = _generate(messages)
            step_data = _parse_json(raw)

            if not step_data:
                log(f"JSON 解析失敗：{raw[:200]}")
                break

            thought = step_data.get("thought", "")
            action  = step_data.get("action", "")
            args    = step_data.get("arguments", {})

            log(f"Thought：{thought}")
            log(f"Action：{action}（{json.dumps(args, ensure_ascii=False)}）")

            if action == "finish":
                url = args.get("url", page.url)
                log(f"任務完成，分享連結：{url}")
                context.close()
                return url

            result = browser.execute(page, action, args, file_path)
            log(f"Observation：{result}")

            history.append({"role": "user",  "content": user_prompt})
            history.append({"role": "model", "content": raw})
            if len(history) > 12:
                history = history[-12:]
            last_result = result

        log(f"達到最大步數 {MAX_STEPS}，回傳當前 URL")
        url = page.url
        context.close()
        return url


def _kill_edge() -> None:
    subprocess.run(["taskkill", "/F", "/IM", "msedge.exe"],         capture_output=True)
    subprocess.run(["taskkill", "/F", "/IM", "msedgewebview2.exe"], capture_output=True)
