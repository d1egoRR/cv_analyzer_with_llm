from unittest.mock import patch

from cv_analyzer.adapters.inbound.api.dependencies import (
    get_cv_evaluator_service,
    get_local_cv_evaluator_service,
    get_pdf_service,
    get_prompt_service,
)
from cv_analyzer.adapters.outbound.llm.fallback_chain_adapter import (
    FallbackCVEvaluationChainAdapter,
)
from cv_analyzer.adapters.outbound.llm.ollama_chain_adapter import (
    OllamaCVEvaluationChainAdapter,
)
from cv_analyzer.application.services.cv_evaluator_service import (
    CVEvaluatorService,
)
from cv_analyzer.application.services.pdf_service import PDFService
from cv_analyzer.application.services.prompt_service import PromptService
from cv_analyzer.infrastructure.config import LLMSettings


def test_get_pdf_service_returns_instance() -> None:
    """Test get_pdf_service factory returns a configured PDFService."""
    service = get_pdf_service()
    assert isinstance(service, PDFService)


def test_get_prompt_service_returns_instance() -> None:
    """Test get_prompt_service factory returns a configured PromptService."""
    service = get_prompt_service()
    assert isinstance(service, PromptService)


def test_get_cv_evaluator_service_wires_fallback_adapter() -> None:
    """Test get_cv_evaluator_service instantiates FallbackCVEvaluationChainAdapter with active providers."""
    mock_settings = LLMSettings(
        enable_gemini=True,
        gemini_api_key="test-gemini-key",
        enable_openai=False,
    )

    get_cv_evaluator_service.cache_clear()

    with patch(
        "cv_analyzer.adapters.inbound.api.dependencies.get_llm_settings",
        return_value=mock_settings,
    ):
        service = get_cv_evaluator_service()

        assert isinstance(service, CVEvaluatorService)
        chain_provider = service._chain_provider
        assert isinstance(chain_provider, FallbackCVEvaluationChainAdapter)
        provider_names = [name for name, _ in chain_provider._providers]
        assert "gemini" in provider_names
        assert "openai" not in provider_names

    get_cv_evaluator_service.cache_clear()


def test_get_local_cv_evaluator_service_wires_ollama_adapter() -> None:
    """Test get_local_cv_evaluator_service instantiates OllamaCVEvaluationChainAdapter exclusively."""
    mock_settings = LLMSettings(
        enable_ollama=True,
        ollama_base_url="http://localhost:11434",
        ollama_model_name="qwen2.5:3b",
        ollama_keep_alive="-1",
    )

    get_local_cv_evaluator_service.cache_clear()

    with patch(
        "cv_analyzer.adapters.inbound.api.dependencies.get_llm_settings",
        return_value=mock_settings,
    ):
        service = get_local_cv_evaluator_service()

        assert isinstance(service, CVEvaluatorService)
        chain_provider = service._chain_provider
        assert isinstance(chain_provider, OllamaCVEvaluationChainAdapter)
        assert chain_provider.provider_name == "ollama"
        assert chain_provider.model_name == "qwen2.5:3b"

    get_local_cv_evaluator_service.cache_clear()
