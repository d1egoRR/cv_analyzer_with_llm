from fastapi import FastAPI

from cv_analyzer.adapters.inbound.api.health_router import (
    router as health_router
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="CV Analyzer API",
        description="API for analyzing CVs using LLMs",
        version="0.1.0",
    )

    app.include_router(health_router)

    return app


app = create_app()
