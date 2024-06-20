import logging

from fastapi import FastAPI, Depends

from src.api.depends import get_apihost_producer
from src.api.router import router


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


app = FastAPI(dependencies=[Depends(get_apihost_producer)])
app.include_router(router)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
