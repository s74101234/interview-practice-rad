import asyncio
import ast
import json
import logging
import re
from datetime import datetime
from pathlib import Path

from services.models import gemini
from services.mcp.tools import search_knowledge, notebooklm
from services.chat.tools import load_tools
import core.app_state as state
from core.app_state import broadcast

logger = logging.getLogger("interview.chat.agent")

# ── Parameters ────────────────────────────────────────────────
MAX_ITERATIONS = 6
_PROMPTS_DIR   = Path(__file__).parent / "prompts"

# ── Tool registry — loaded from schemas/ JSON files ────────────
_TOOLS = load_tools()


# ── Prompt loader ──────────────────────────────────────────────
def _load_prompt(filename: str) -> str:
    return (_PROMPTS_DIR / filename).read_text(encoding="utf-8").strip()


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


def _fill_template(template: str, **kwargs) -> str:
    return re.sub(
        r"\{([a-zA-Z_]\w*)\}",
        lambda m: str(kwargs.get(m.group(1), m.group(0))),
        template,
    )


# ── JSON parser ────────────────────────────────────────────────
def _parse_json(raw: str) -> dict | None:
    start = raw.find("{")
    if start == -1:
        return None
    depth, in_str, escape, end = 0, False, False, -1
    for i, ch in enumerate(raw[start:], start):
        if escape:
            escape = False; continue
        if ch == "\\" and in_str:
            escape = True; continue
        if ch == '"':
            in_str = not in_str; continue
        if in_str:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                end = i; break
    candidate = raw[start: end + 1] if end != -1 else raw[start:]
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    try:
        result = ast.literal_eval(candidate)
        if isinstance(result, dict):
            return result
    except Exception:
        pass
    return None


# ── Gemini call ────────────────────────────────────────────────
async def _generate(messages: list[dict], system: str) -> str:
    return await asyncio.to_thread(gemini.generate_text, messages, system)


# ── Tool execution ─────────────────────────────────────────────
async def _execute_tool(name: str, args: dict) -> str:
    if name == "search_knowledge":
        query = args.get("query", "")
        top_k = int(args.get("top_k", 5))
        await broadcast("log", {"message": f"查詢知識庫：「{query}」"})
        results = await asyncio.to_thread(search_knowledge.run, query, top_k)
        await broadcast("log", {"message": f"取得 {len(results)} 筆相關段落（第 {', '.join(str(r['page']) for r in results)} 頁）"})
        return "\n\n".join(
            f"來源：{r['source']}，第 {r['page']} 頁\n{r['text']}" for r in results
        )

    if name == "create_notebooklm":
        if not state.uploaded_file_path:
            return "尚未上傳任何文件，請先上傳後再建立 NotebookLM。"
        title = args.get("title", "Interview Practice Notebook")
        await broadcast("log", {"message": f"[NotebookLM] 啟動瀏覽器自動化，建立筆記本：{title}"})
        try:
            loop = asyncio.get_event_loop()

            def sync_log(message: str) -> None:
                asyncio.run_coroutine_threadsafe(
                    broadcast("log", {"message": message}), loop
                )

            url = await asyncio.to_thread(notebooklm.run, state.uploaded_file_path, title, sync_log)
            await broadcast("log", {"message": f"[NotebookLM] 完成，筆記本連結：{url}"})
            return f"NotebookLM 筆記本已建立，請點此開啟：{url}"
        except Exception as e:
            import traceback
            detail = str(e) or repr(e) or type(e).__name__
            tb = traceback.format_exc()
            logger.error("[NotebookLM] 自動化失敗\n%s", tb)
            await broadcast("log", {"message": f"[NotebookLM] 錯誤類型：{type(e).__name__}"})
            await broadcast("log", {"message": f"[NotebookLM] 錯誤訊息：{detail}"})
            await broadcast("log", {"message": f"[NotebookLM] Traceback：\n{tb}"})
            raise

    return f"未知工具：{name}"


# ── ReAct loop ─────────────────────────────────────────────────
async def chat(history: list[dict], user_message: str) -> dict:
    state.cancel_event.clear()
    await broadcast("log", {"message": f"[使用者] {user_message}"})
    await broadcast("log", {"message": f"[系統] 啟動 ReAct 迴圈，模型：{gemini.MODEL}"})
    await broadcast("log", {"message": f"[系統] 知識庫狀態：{'已就緒（' + state.last_filename + '）' if state.last_filename else '尚未上傳文件'}"})

    today          = datetime.now().strftime("%Y-%m-%d %H:%M")
    system_desc    = _load_prompt("prompt_system.md")
    template       = _load_prompt("prompt_react.md")
    system         = _fill_template(
        template,
        system_description=system_desc,
        today=today,
        system_context=(
            f"使用模型：{gemini.MODEL}\n"
            "知識庫狀態：" + ("已就緒（" + state.last_filename + "）" if state.last_filename else "尚未上傳文件")
        ),
        tools_context=_build_tools_context(_TOOLS),
    )

    messages: list[dict] = [
        {"role": m["role"], "content": m["content"]}
        for m in history
    ]
    messages.append({"role": "user", "content": user_message})

    tool_label = None

    for iteration in range(MAX_ITERATIONS):
        logger.info("[ReAct] 迭代 %d / %d", iteration + 1, MAX_ITERATIONS)
        await broadcast("log", {"message": f"[第 {iteration + 1} 輪] 模型推論中..."})

        raw  = await _generate(messages, system)
        step = _parse_json(raw)

        if not step:
            logger.warning("[ReAct] JSON 解析失敗：%s", raw)
            await broadcast("log", {"message": f"[錯誤] 模型輸出無法解析，完整輸出如下：\n{raw}"})
            return {"content": "抱歉，我無法理解這個問題，請重新描述。", "tool": None}

        # 直接回答
        if "answer" in step:
            answer = str(step["answer"]).strip()
            await broadcast("log", {"message": f"[第 {iteration + 1} 輪] 模型直接回答（{len(answer)} 字）"})
            logger.info("[ReAct] 回答完成，長度=%d 字", len(answer))
            return {"content": answer, "tool": tool_label}

        action  = step.get("action", "")
        args    = {k: v for k, v in (step.get("arguments") or {}).items() if v is not None and v != ""}
        thought = step.get("thought", "")

        if not action:
            await broadcast("log", {"message": "[錯誤] 模型未指定 action，終止迴圈"})
            return {"content": "抱歉，我無法理解這個問題，請重新描述。", "tool": None}

        await broadcast("log", {"message": f"[第 {iteration + 1} 輪] Thought：{thought}"})
        await broadcast("log", {"message": f"[第 {iteration + 1} 輪] Action：{action}，參數：{json.dumps(args, ensure_ascii=False)}"})
        tool_label = action

        observation = await _execute_tool(action, args)

        preview = observation[:200] + "..." if len(observation) > 200 else observation
        await broadcast("log", {"message": f"[第 {iteration + 1} 輪] Observation：{preview}"})

        obs_message = (
            f"Thought：{thought}\n"
            f"Action：{action}\n"
            f"Observation：\n{observation}\n\n"
            f"請根據以上觀察繼續推理，輸出下一步 JSON。"
        )
        messages.append({"role": "model", "content": raw})
        messages.append({"role": "user", "content": obs_message})

    logger.warning("[ReAct] 達到最大迭代次數 %d", MAX_ITERATIONS)
    await broadcast("log", {"message": f"[系統] 達到最大迭代次數 {MAX_ITERATIONS}，強制終止"})
    return {"content": "處理超時，請重新提問。", "tool": tool_label}
