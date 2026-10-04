from unittest.mock import MagicMock, patch

import pytest

from cv_analyzer.adapters.outbound.llm.exceptions import LLMProviderError
from cv_analyzer.adapters.outbound.llm.gemini_chain_adapter import (
    GeminiCVEvaluationChainAdapter,
)
from cv_analyzer.application.ports.prompt_generator import (
    PromptGeneratorPort,
)
from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult


@patch("cv_analyzer.adapters.outbound.llm.gemini_chain_adapter.ChatGoogleGenerativeAI")
def test_create_chain_uses_default_prompt_from_generator(
    mock_chat_gemini: MagicMock,
) -> None:
    """Test that create_chain uses the injected PromptGeneratorPort when no custom prompt is given."""
    mock_prompt = MagicMock()
    mock_generator = MagicMock(spec=PromptGeneratorPort)
    mock_generator.generate_cv_analysis_prompt.return_value = mock_prompt

    mock_structured_llm = MagicMock()
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm
    mock_chat_gemini.return_value = mock_llm_instance

    adapter = GeminiCVEvaluationChainAdapter(
        prompt_generator=mock_generator,
        api_key="gemini-test-key",
    )
    adapter.create_chain()

    mock_generator.generate_cv_analysis_prompt.assert_called_once()


@patch("cv_analyzer.adapters.outbound.llm.gemini_chain_adapter.ChatGoogleGenerativeAI")
def test_create_chain_uses_custom_prompt_template(
    mock_chat_gemini: MagicMock,
) -> None:
    """Test that create_chain uses the provided prompt_template instead of the generator."""
    mock_generator = MagicMock(spec=PromptGeneratorPort)

    mock_structured_llm = MagicMock()
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm
    mock_chat_gemini.return_value = mock_llm_instance

    custom_prompt = MagicMock()
    adapter = GeminiCVEvaluationChainAdapter(
        prompt_generator=mock_generator,
        api_key="gemini-test-key",
    )
    adapter.create_chain(prompt_template=custom_prompt)

    mock_generator.generate_cv_analysis_prompt.assert_not_called()


@patch("cv_analyzer.adapters.outbound.llm.gemini_chain_adapter.ChatGoogleGenerativeAI")
def test_create_chain_calls_with_structured_output(
    mock_chat_gemini: MagicMock,
) -> None:
    """Test that create_chain binds CVAnalysisResult schema."""
    mock_generator = MagicMock(spec=PromptGeneratorPort)
    mock_generator.generate_cv_analysis_prompt.return_value = MagicMock()

    mock_llm_instance = MagicMock()
    mock_chat_gemini.return_value = mock_llm_instance

    adapter = GeminiCVEvaluationChainAdapter(
        prompt_generator=mock_generator,
        api_key="gemini-test-key",
    )
    adapter.create_chain()

    mock_llm_instance.with_structured_output.assert_called_once_with(CVAnalysisResult)


def test_create_chain_missing_api_key_raises_error() -> None:
    """Test that missing GEMINI_API_KEY raises LLMProviderError."""
    mock_generator = MagicMock(spec=PromptGeneratorPort)
    adapter = GeminiCVEvaluationChainAdapter(
        prompt_generator=mock_generator, 
        api_key=""
    )

    with pytest.raises(LLMProviderError) as exc_info:
        adapter.create_chain()

    assert "GEMINI_API_KEY is not configured" in str(exc_info.value)


@patch("cv_analyzer.adapters.outbound.llm.gemini_chain_adapter.ChatGoogleGenerativeAI")
def test_create_chain_sets_max_retries_zero(mock_chat_gemini: MagicMock) -> None:
    """Test that ChatGoogleGenerativeAI is initialized with max_retries=0."""
    mock_generator = MagicMock(spec=PromptGeneratorPort)
    mock_generator.generate_cv_analysis_prompt.return_value = MagicMock()

    mock_llm_instance = MagicMock()
    mock_chat_gemini.return_value = mock_llm_instance

    adapter = GeminiCVEvaluationChainAdapter(
        prompt_generator=mock_generator,
        api_key="gemini-test-key",
        model_name="gemini-2.0-flash",
        timeout=25.0,
    )
    adapter.create_chain()

    mock_chat_gemini.assert_called_once_with(
        model="gemini-2.0-flash",
        google_api_key="gemini-test-key",
        temperature=0.0,
        timeout=25.0,
        max_retries=0,
    )


def test_gemini_adapter_properties() -> None:
    """Test provider_name and model_name properties on Gemini adapter."""
    mock_generator = MagicMock(spec=PromptGeneratorPort)
    adapter = GeminiCVEvaluationChainAdapter(
        prompt_generator=mock_generator,
        api_key="gemini-test-key",
        model_name="gemini-1.5-pro",
    )
    assert adapter.provider_name == "gemini"
    assert adapter.model_name == "gemini-1.5-pro"
