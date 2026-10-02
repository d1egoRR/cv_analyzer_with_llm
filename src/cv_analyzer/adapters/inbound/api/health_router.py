from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    status: str


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Health Check"
)
def health_check() -> HealthResponse:
    return HealthResponse(status="ok")
