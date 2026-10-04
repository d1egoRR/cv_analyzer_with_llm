from io import BytesIO
from unittest.mock import MagicMock

from fastapi.testclient import TestClient

from cv_analyzer.domain.exceptions import (
    CVEvaluationError,
    EmptyPDFError,
    PDFExtractionError,
)
from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult


def test_analyze_cv_success(
    client: TestClient,
    mock_services: dict[str, MagicMock],
    sample_cv_result: CVAnalysisResult,
) -> None:
    """Test successful CV analysis workflow coordinating all services."""
    pdf_bytes = b"%PDF-1.4 mock pdf binary content"
    files = {"cv_file": ("test_cv.pdf", BytesIO(pdf_bytes), "application/pdf")}
    data = {
        "job_description": "Looking for a Senior Python Developer with FastAPI experience."
    }

    response = client.post("/cv/analyze", data=data, files=files)

    assert response.status_code == 200
    json_data = response.json()
    assert json_data["candidate_name"] == sample_cv_result.candidate_name
    assert json_data["years_of_experience"] == sample_cv_result.years_of_experience
    assert json_data["key_skills"] == sample_cv_result.key_skills
    assert json_data["match_percentage"] == sample_cv_result.match_percentage
    assert json_data["provider"] == sample_cv_result.provider
    assert json_data["model"] == sample_cv_result.model

    mock_services["pdf_service"].extract_text_from_stream.assert_called_once()
    mock_services["prompt_service"].create_cv_analysis_prompt.assert_called_once()
    mock_services["evaluator_service"].evaluate.assert_called_once_with(
        job_description="Looking for a Senior Python Developer with FastAPI experience.",
        cv_text="Extracted CV text",
        prompt_template=mock_services["prompt_service"].create_cv_analysis_prompt.return_value,
    )


def test_analyze_cv_rejects_empty_job_description(client: TestClient) -> None:
    """Test that an empty or whitespace-only job description returns 400 Bad Request."""
    pdf_bytes = b"%PDF-1.4 mock pdf content"
    files = {"cv_file": ("test_cv.pdf", BytesIO(pdf_bytes), "application/pdf")}
    data = {"job_description": "          "}

    response = client.post("/cv/analyze", data=data, files=files)

    assert response.status_code == 400
    assert "Job description text cannot be empty" in response.json()["detail"]


def test_analyze_cv_rejects_non_pdf_file(client: TestClient) -> None:
    """Test that uploading a non-PDF file returns 400 Bad Request."""
    txt_bytes = b"This is a plain text file, not a PDF."
    files = {"cv_file": ("cv.txt", BytesIO(txt_bytes), "text/plain")}
    data = {"job_description": "Looking for a Python Developer."}

    response = client.post("/cv/analyze", data=data, files=files)

    assert response.status_code == 400
    assert "Only PDF files (.pdf) are supported" in response.json()["detail"]


def test_analyze_cv_handles_empty_pdf_error(
    client: TestClient,
    mock_services: dict[str, MagicMock],
) -> None:
    """Test that EmptyPDFError raised by PDFService returns 400 Bad Request."""
    mock_services["pdf_service"].extract_text_from_stream.side_effect = (
        EmptyPDFError("The provided PDF file contains no extractable text.")
    )

    pdf_bytes = b"%PDF-1.4 empty pdf"
    files = {"cv_file": ("empty.pdf", BytesIO(pdf_bytes), "application/pdf")}
    data = {"job_description": "Looking for a Python Developer with FastAPI."}

    response = client.post("/cv/analyze", data=data, files=files)

    assert response.status_code == 400
    assert "no extractable text" in response.json()["detail"]


def test_analyze_cv_handles_pdf_extraction_error(
    client: TestClient,
    mock_services: dict[str, MagicMock],
) -> None:
    """Test that PDFExtractionError raised by PDFService returns 422 Unprocessable Entity."""
    mock_services["pdf_service"].extract_text_from_stream.side_effect = (
        PDFExtractionError("Corrupted stream")
    )

    pdf_bytes = b"%PDF-1.4 corrupted"
    files = {"cv_file": ("corrupt.pdf", BytesIO(pdf_bytes), "application/pdf")}
    data = {"job_description": "Looking for a Python Developer with FastAPI."}

    response = client.post("/cv/analyze", data=data, files=files)

    assert response.status_code == 422
    assert "Failed to process PDF" in response.json()["detail"]


def test_analyze_cv_handles_cv_evaluation_error(
    client: TestClient,
    mock_services: dict[str, MagicMock],
) -> None:
    """Test that CVEvaluationError raised by CVEvaluatorService returns 502 Bad Gateway."""
    mock_services["evaluator_service"].evaluate.side_effect = CVEvaluationError(
        "LLM API timeout"
    )

    pdf_bytes = b"%PDF-1.4 valid pdf"
    files = {"cv_file": ("valid.pdf", BytesIO(pdf_bytes), "application/pdf")}
    data = {"job_description": "Looking for a Python Developer with FastAPI."}

    response = client.post("/cv/analyze", data=data, files=files)

    assert response.status_code == 502
    assert "CV evaluation failed" in response.json()["detail"]
