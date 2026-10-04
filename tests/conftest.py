from collections.abc import Generator
from unittest.mock import MagicMock

import pytest
from fastapi.testclient import TestClient

from cv_analyzer.adapters.inbound.api.dependencies import (
    get_cv_evaluator_service,
    get_pdf_service,
    get_prompt_service,
)
from cv_analyzer.application.services.cv_evaluator_service import (
    CVEvaluatorService,
)
from cv_analyzer.application.services.pdf_service import PDFService
from cv_analyzer.application.services.prompt_service import PromptService
from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult
from cv_analyzer.main import app


@pytest.fixture(autouse=True)
def isolate_test_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ensure all tests run in an isolated environment without real .env credentials."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.delenv("OPENROUTER_API_KEY", raising=False)
    monkeypatch.delenv("MISTRAL_API_KEY", raising=False)
    monkeypatch.setenv("ENABLE_GEMINI", "false")
    monkeypatch.setenv("ENABLE_OPENAI", "false")
    monkeypatch.setenv("ENABLE_GROQ", "false")
    monkeypatch.setenv("ENABLE_OPENROUTER", "false")
    monkeypatch.setenv("ENABLE_MISTRAL", "false")


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    """TestClient fixture that guarantees dependency overrides are cleared after each test."""
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_pdf_service() -> MagicMock:
    """Fixture providing a mock PDFService."""
    mock = MagicMock(spec=PDFService)
    mock.extract_text_from_stream.return_value = "Extracted CV text"
    return mock


@pytest.fixture
def mock_prompt_service() -> MagicMock:
    """Fixture providing a mock PromptService."""
    mock = MagicMock(spec=PromptService)
    mock.create_cv_analysis_prompt.return_value = MagicMock()
    return mock


@pytest.fixture
def sample_cv_result() -> CVAnalysisResult:
    """Fixture providing a valid CVAnalysisResult domain instance."""
    return CVAnalysisResult(
        candidate_name="Jane Doe",
        years_of_experience=5.0,
        key_skills=["Python", "FastAPI", "Docker"],
        education="B.S. in Computer Science",
        relevant_experience="5 years in backend development",
        strengths=["API Architecture", "Testing"],
        areas_for_improvement=["Kubernetes"],
        match_percentage=88,
    )


@pytest.fixture
def mock_evaluator_service(
    sample_cv_result: CVAnalysisResult,
) -> MagicMock:
    """Fixture providing a mock CVEvaluatorService configured with sample_cv_result."""
    mock = MagicMock(spec=CVEvaluatorService)
    mock.evaluate.return_value = sample_cv_result
    return mock


@pytest.fixture
def mock_services(
    mock_pdf_service: MagicMock,
    mock_prompt_service: MagicMock,
    mock_evaluator_service: MagicMock,
) -> dict[str, MagicMock]:
    """Automatically wire mock services into FastAPI dependency overrides.

    Yields a dictionary with access to all mocks for assertions or custom behavior.
    """
    app.dependency_overrides[get_pdf_service] = lambda: mock_pdf_service
    app.dependency_overrides[get_prompt_service] = lambda: mock_prompt_service
    app.dependency_overrides[get_cv_evaluator_service] = (
        lambda: mock_evaluator_service
    )

    return {
        "pdf_service": mock_pdf_service,
        "prompt_service": mock_prompt_service,
        "evaluator_service": mock_evaluator_service,
    }
