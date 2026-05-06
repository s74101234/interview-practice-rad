from fastapi import APIRouter
from core.schemas import ChatRequest, ChatResponse, ChatMessage
from services.chat.chat_agent import chat

router = APIRouter()

_history: list[dict] = []


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    global _history

    result = await chat(_history, req.message)

    from google.genai import types
    _history.append(types.Content(role="user", parts=[types.Part(text=req.message)]))
    _history.append(types.Content(role="model", parts=[types.Part(text=result["content"])]))

    if len(_history) > 12:
        _history = _history[-12:]

    return ChatResponse(
        message=ChatMessage(
            role="assistant",
            content=result["content"],
            tool=result.get("tool"),
        )
    )
