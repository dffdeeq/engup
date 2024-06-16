from fastapi import APIRouter, Request

router = APIRouter(tags=["Authentication"])


@router.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    print(payload)
    return {"status": "success"}
