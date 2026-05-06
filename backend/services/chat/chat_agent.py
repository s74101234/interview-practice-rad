import asyncio
from google.genai import types
from services.models import gemini
from services.mcp.tools import search_knowledge, create_notebooklm
import core.app_state as state

SYSTEM = (
    "你是一個文件助理，協助使用者查詢已上傳文件的內容，或建立 NotebookLM 筆記本。"
    "若使用者詢問文件內容，請使用 search_knowledge 工具搜尋後回答。"
    "若使用者提及建立簡報、分享、筆記本，請使用 create_notebooklm 工具。"
    "若知識庫尚未建立，請提示使用者先上傳文件。"
)


async def _execute_tool(name: str, args: dict) -> tuple[str, str]:
    """Execute a tool and return (result_text, tool_label)."""
    if name == "search_knowledge":
        query = args.get("query", "")
        top_k = args.get("top_k", 5)
        results = search_knowledge.run(query, top_k)
        context = "\n\n".join(
            f"來源：{r['source']}，第 {r['page']} 頁\n{r['text']}" for r in results
        )
        return context, "已查詢知識庫"

    elif name == "create_notebooklm":
        if not state.uploaded_file_path:
            return "尚未上傳任何文件。", "create_notebooklm"
        title = args.get("title", "DocMind Notebook")
        url = await create_notebooklm.run(state.uploaded_file_path, title)
        return url, "已建立 NotebookLM"

    return "", name


async def chat(history: list[dict], user_message: str) -> dict:
    """
    history: [{"role": "user"|"model", "parts": [{"text": "..."}]}]
    Returns: {"content": str, "tool": str | None}
    """
    contents = list(history) + [
        types.Content(role="user", parts=[types.Part(text=user_message)])
    ]

    response = gemini.generate(contents, system=SYSTEM)
    candidate = response.candidates[0]
    part = candidate.content.parts[0]

    # Function call requested
    if part.function_call:
        fn_name = part.function_call.name
        fn_args = dict(part.function_call.args)

        tool_result, tool_label = await _execute_tool(fn_name, fn_args)

        # Send tool result back to Gemini
        contents.append(candidate.content)
        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        function_response=types.FunctionResponse(
                            name=fn_name,
                            response={"result": tool_result},
                        )
                    )
                ],
            )
        )

        final_response = gemini.generate(contents, system=SYSTEM)
        final_text = final_response.candidates[0].content.parts[0].text
        return {"content": final_text, "tool": tool_label}

    return {"content": part.text, "tool": None}
