from fastapi import APIRouter
from core.schemas import ChatRequest, ChatResponse, ChatMessage
from services.chat.chat_agent import chat

router = APIRouter()

_history: list[dict] = []


@router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(req: ChatRequest):
    global _history

    try:
        result = await chat(_history, req.message)
    except Exception as e:
        return ChatResponse(
            message=ChatMessage(role="assistant", content=f"⚠️ {e}", tool=None)
        )

    _history.append({"role": "user", "content": req.message})
    _history.append({"role": "model", "content": result["content"]})

    if len(_history) > 12:
        _history = _history[-12:]

    return ChatResponse(
        message=ChatMessage(
            role="assistant",
            content=result["content"],
            tool=result.get("tool"),
        )
    )
