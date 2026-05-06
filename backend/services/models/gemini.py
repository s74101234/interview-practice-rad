from google import genai
from google.genai import types
from core.config import settings

_client = genai.Client(api_key=settings.gemini_api_key)
MODEL = "gemini-2.0-flash"

TOOLS = [
    types.Tool(
        function_declarations=[
            types.FunctionDeclaration(
                name="search_knowledge",
                description="搜尋已上傳文件的知識庫，回傳相關段落。使用者詢問文件內容時呼叫此工具。",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "query": types.Schema(type=types.Type.STRING, description="搜尋查詢字串"),
                        "top_k": types.Schema(type=types.Type.INTEGER, description="回傳筆數，預設 5"),
                    },
                    required=["query"],
                ),
            ),
            types.FunctionDeclaration(
                name="create_notebooklm",
                description="將已上傳的文件建立為 NotebookLM 筆記本，回傳可分享連結。使用者提及建立簡報、分享、筆記本時呼叫此工具。",
                parameters=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "title": types.Schema(type=types.Type.STRING, description="筆記本標題"),
                    },
                    required=["title"],
                ),
            ),
        ]
    )
]


def generate(contents: list, system: str | None = None) -> types.GenerateContentResponse:
    config = types.GenerateContentConfig(tools=TOOLS)
    if system:
        config.system_instruction = system
    return _client.models.generate_content(
        model=MODEL,
        contents=contents,
        config=config,
    )
