from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import upload, chat, status, mcp

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
app.include_router(mcp.router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
