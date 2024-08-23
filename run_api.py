import logging

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from src.api.depends import get_apihost_producer, get_metrics_repo
from src.api.router import router


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

origins = [
    "https://ielts-offical.com",
]


app = FastAPI(dependencies=[Depends(get_apihost_producer), Depends(get_metrics_repo), ])
app.include_router(router)

app.add_middleware(
    CORSMiddleware,  # noqa
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
