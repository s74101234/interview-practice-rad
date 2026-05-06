from fastapi import APIRouter
from services.mcp.server import mcp

router = APIRouter()

app = mcp.get_asgi_app()


@router.mount("/mcp")
async def mcp_endpoint(scope, receive, send):
    await app(scope, receive, send)
