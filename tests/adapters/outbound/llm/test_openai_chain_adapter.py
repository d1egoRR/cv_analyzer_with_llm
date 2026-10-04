from unittest.mock import MagicMock, patch

import pytest

from cv_analyzer.adapters.outbound.llm.exceptions import LLMProviderError
from cv_analyzer.adapters.outbound.llm.openai_chain_adapter import (
    OpenAICVEvaluationChainAdapter,
)
from cv_analyzer.application.ports.prompt_generator import (
    PromptGeneratorPort,
)
from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult


@patch("cv_analyzer.adapters.outbound.llm.openai_chain_adapter.ChatOpenAI")
def test_create_chain_uses_default_prompt_from_generator(mock_chat_openai: MagicMock) -> None:
    """Test that create_chain uses the injected PromptGeneratorPort when no prompt_template is given."""
    mock_prompt = MagicMock()
    mock_generator = MagicMock(spec=PromptGeneratorPort)
    mock_generator.generate_cv_analysis_prompt.return_value = mock_prompt

    mock_structured_llm = MagicMock()
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm
    mock_chat_openai.return_value = mock_llm_instance

    adapter = OpenAICVEvaluationChainAdapter(
        prompt_generator=mock_generator, api_key="sk-test-key"
    )
    adapter.create_chain()

    mock_generator.generate_cv_analysis_prompt.assert_called_once()


@patch("cv_analyzer.adapters.outbound.llm.openai_chain_adapter.ChatOpenAI")
def test_create_chain_uses_custom_prompt_template(mock_chat_openai: MagicMock) -> None:
    """Test that create_chain uses the provided prompt_template instead of the generator."""
    mock_generator = MagicMock(spec=PromptGeneratorPort)

    mock_structured_llm = MagicMock()
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm
    mock_chat_openai.return_value = mock_llm_instance

    custom_prompt = MagicMock()
    adapter = OpenAICVEvaluationChainAdapter(
        prompt_generator=mock_generator, api_key="sk-test-key"
    )
    adapter.create_chain(prompt_template=custom_prompt)

    mock_generator.generate_cv_analysis_prompt.assert_not_called()


@patch("cv_analyzer.adapters.outbound.llm.openai_chain_adapter.ChatOpenAI")
def test_create_chain_calls_with_structured_output(mock_chat_openai: MagicMock) -> None:
    """Test that create_chain calls with_structured_output with CVAnalysisResult."""
    mock_generator = MagicMock(spec=PromptGeneratorPort)
    mock_generator.generate_cv_analysis_prompt.return_value = MagicMock()

    mock_llm_instance = MagicMock()
    mock_chat_openai.return_value = mock_llm_instance

    adapter = OpenAICVEvaluationChainAdapter(
        prompt_generator=mock_generator, api_key="sk-test-key"
    )
    adapter.create_chain()

    mock_llm_instance.with_structured_output.assert_called_once_with(CVAnalysisResult)


def test_create_chain_missing_api_key_raises_error() -> None:
    """Test that missing API key raises LLMProviderError."""
    mock_generator = MagicMock(spec=PromptGeneratorPort)
    adapter = OpenAICVEvaluationChainAdapter(
        prompt_generator=mock_generator, api_key=""
    )

    with pytest.raises(LLMProviderError) as exc_info:
        adapter.create_chain()

    assert "API key for provider 'openai' is not configured" in str(exc_info.value)


@patch("cv_analyzer.adapters.outbound.llm.openai_chain_adapter.ChatOpenAI")
def test_create_chain_configures_max_retries_zero_and_base_url(
    mock_chat_openai: MagicMock,
) -> None:
    """Test that max_retries is set to 0 and base_url is forwarded if configured."""
    mock_generator = MagicMock(spec=PromptGeneratorPort)
    mock_generator.generate_cv_analysis_prompt.return_value = MagicMock()

    mock_llm_instance = MagicMock()
    mock_chat_openai.return_value = mock_llm_instance

    adapter = OpenAICVEvaluationChainAdapter(
        prompt_generator=mock_generator,
        api_key="sk-test-key",
        base_url="https://api.groq.com/openai/v1",
        provider_name="groq",
    )
    adapter.create_chain()

    mock_chat_openai.assert_called_once()
    _, kwargs = mock_chat_openai.call_args
    assert kwargs["max_retries"] == 0
    assert kwargs["base_url"] == "https://api.groq.com/openai/v1"


def test_openai_adapter_properties() -> None:
    """Test provider_name and model_name properties on OpenAI adapter."""
    mock_generator = MagicMock(spec=PromptGeneratorPort)
    adapter = OpenAICVEvaluationChainAdapter(
        prompt_generator=mock_generator,
        api_key="sk-test-key",
        model_name="gpt-4o",
        provider_name="openai",
    )
    assert adapter.provider_name == "openai"
    assert adapter.model_name == "gpt-4o"
