from __future__ import annotations

from typing import Annotated

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)

from cv_analyzer.adapters.inbound.api.dependencies import (
    get_cv_evaluator_service,
    get_pdf_service,
    get_prompt_service,
)
from cv_analyzer.adapters.inbound.api.schemas import (
    CVAnalysisResponse,
    ErrorResponse,
)
from cv_analyzer.application.services.cv_evaluator_service import (
    CVEvaluatorService,
)
from cv_analyzer.application.services.pdf_service import PDFService
from cv_analyzer.application.services.prompt_service import PromptService
from cv_analyzer.domain.exceptions import (
    CVEvaluationError,
    EmptyPDFError,
    PDFExtractionError,
)

router = APIRouter(tags=["CV Analysis"])


@router.post(
    "/cv/analyze",
    response_model=CVAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Analyze Candidate CV against Job Description",
    description=(
        "Upload a CV in PDF format and provide a target job description. "
        "The CV is processed entirely in memory without being stored on disk. "
        "Text is extracted, processed with prompt templates, and evaluated "
        "against the job description using LLM to generate a structured report."
    ),
    responses={
        status.HTTP_200_OK: {
            "description": "Successful CV evaluation against the job description.",
            "model": CVAnalysisResponse,
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "Invalid file format, empty PDF, or invalid job description.",
            "model": ErrorResponse,
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Corrupt or unreadable PDF file.",
            "model": ErrorResponse,
        },
        status.HTTP_502_BAD_GATEWAY: {
            "description": "LLM evaluation service failure.",
            "model": ErrorResponse,
        },
    },
)
async def analyze_cv(
    job_description: Annotated[
        str,
        Form(
            description="Detailed job description and requirements for the position.",
            min_length=10,
            examples=[
                (
                    "We are seeking a Senior Python Engineer with at least "
                    "4 years of experience in FastAPI, Docker, and LLM integrations. "
                    "Responsibilities include designing clean architectures and APIs."
                )
            ],
        ),
    ],
    cv_file: Annotated[
        UploadFile,
        File(
            description="Candidate CV document in PDF format (.pdf).",
        ),
    ],
    pdf_service: Annotated[PDFService, Depends(get_pdf_service)],
    prompt_service: Annotated[PromptService, Depends(get_prompt_service)],
    evaluator_service: Annotated[
        CVEvaluatorService, Depends(get_cv_evaluator_service)
    ],
) -> CVAnalysisResponse:
    """Analyze an uploaded CV against a job description.

    Args:
        job_description: Target job requirements text.
        cv_file: Uploaded candidate PDF CV.
        pdf_service: Injected PDF extraction service.
        prompt_service: Injected prompt template service.
        evaluator_service: Injected CV evaluation service.

    Returns:
        Structured evaluation metrics in CVAnalysisResponse.

    Raises:
        HTTPException: On validation, extraction, or evaluation errors.
    """
    if not job_description.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description text cannot be empty or whitespace.",
        )

    filename = (cv_file.filename or "").lower()
    content_type = cv_file.content_type or ""

    if not filename.endswith(".pdf") and content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file format. Only PDF files (.pdf) are supported.",
        )

    try:
        cv_text = pdf_service.extract_text_from_stream(cv_file.file)
    except EmptyPDFError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    except PDFExtractionError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Failed to process PDF: {exc}",
        ) from exc
    finally:
        await cv_file.close()

    prompt_template = prompt_service.create_cv_analysis_prompt()

    try:
        domain_result = evaluator_service.evaluate(
            job_description=job_description,
            cv_text=cv_text,
            prompt_template=prompt_template,
        )
    except CVEvaluationError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"CV evaluation failed: {exc}",
        ) from exc

    return CVAnalysisResponse.from_domain(domain_result)
