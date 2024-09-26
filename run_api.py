import logging

from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from src.api.depends import get_apihost_producer, get_metrics_repo, get_question_service
from src.api.mp3tts.router import router as mp3tts_router
from src.api.metrics.router import router as metrics_router
from src.api.question.router import router as question_router


def create_app() -> FastAPI:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    app = FastAPI(dependencies=[
        Depends(get_apihost_producer),
        Depends(get_metrics_repo),
        Depends(get_question_service)
    ])

    app.include_router(mp3tts_router)
    app.include_router(metrics_router)
    app.include_router(question_router)

    origins = ["https://ielts-offical.com"]
    app.add_middleware(
        CORSMiddleware,  # noqa
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
