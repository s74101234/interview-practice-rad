from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import upload, chat, status

app = FastAPI(title="DocMind")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(status.router)

# MCP server — optional, mount only if FastMCP ASGI API is compatible
try:
    from services.mcp.server import mcp

    if hasattr(mcp, "http_app"):
        app.mount("/mcp", mcp.http_app(path="/"))
    elif hasattr(mcp, "get_asgi_app"):
        app.mount("/mcp", mcp.get_asgi_app())
    else:
        raise AttributeError("No compatible ASGI method on FastMCP")
except Exception as e:
    import warnings
    warnings.warn(f"MCP server skipped: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
