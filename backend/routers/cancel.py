from fastapi import APIRouter
import core.app_state as state

router = APIRouter()


@router.post("/cancel")
async def cancel():
    state.cancel_event.set()
    return {"cancelled": True}
