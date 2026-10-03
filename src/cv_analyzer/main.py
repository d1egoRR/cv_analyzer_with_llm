from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from cv_analyzer.adapters.inbound.api.cv_analysis_router import (
    router as cv_analysis_router,
)
from cv_analyzer.adapters.inbound.api.health_router import (
    router as health_router,
)


def create_app() -> FastAPI:
    app = FastAPI(
        title="CV Analyzer API",
        description="API for analyzing CVs using LLMs",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.include_router(health_router)
    app.include_router(cv_analysis_router)

    @app.get("/", include_in_schema=False)
    def root_redirect() -> RedirectResponse:
        return RedirectResponse(url="/docs")

    return app


app = create_app()
