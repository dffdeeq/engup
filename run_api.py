import logging

from fastapi import FastAPI, Request


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


app = FastAPI()


@app.post("/webhook")
async def webhook(request: Request):
    payload = await request.json()
    logging.info(payload)
    return {"status": "success"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
