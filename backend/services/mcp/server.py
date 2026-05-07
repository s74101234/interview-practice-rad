from fastmcp import FastMCP
from services.mcp.tools import search_knowledge, notebooklm
import core.app_state as state

mcp = FastMCP("Interview Practice")


@mcp.tool()
def search_knowledge_tool(query: str, top_k: int = 5) -> list[dict]:
    """搜尋已上傳文件的知識庫，回傳相關段落"""
    return search_knowledge.run(query, top_k)


@mcp.tool()
async def create_notebooklm_tool(title: str) -> dict:
    """將已上傳的文件建立為 NotebookLM 筆記本，回傳可分享連結"""
    if not state.uploaded_file_path:
        return {"error": "尚未上傳任何文件"}
    url = await notebooklm.run(state.uploaded_file_path, title)
    return {"notebook_url": url}
