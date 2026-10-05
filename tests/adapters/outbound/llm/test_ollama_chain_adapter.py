from unittest.mock import MagicMock, patch

from cv_analyzer.adapters.outbound.llm.ollama_chain_adapter import (
    OllamaCVEvaluationChainAdapter,
)
from cv_analyzer.application.ports.prompt_generator import (
    PromptGeneratorPort,
)
from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult


def test_ollama_adapter_properties() -> None:
    """Test provider_name and model_name properties on Ollama adapter."""
    mock_generator = MagicMock(spec=PromptGeneratorPort)
    adapter = OllamaCVEvaluationChainAdapter(
        prompt_generator=mock_generator,
        model_name="qwen2.5:3b",
        base_url="http://localhost:11434",
        keep_alive="-1",
    )
    assert adapter.provider_name == "ollama"
    assert adapter.model_name == "qwen2.5:3b"


@patch("cv_analyzer.adapters.outbound.llm.ollama_chain_adapter.ChatOllama")
def test_create_chain_uses_default_prompt_from_generator(
    mock_chat_ollama: MagicMock,
) -> None:
    """Test that create_chain uses the injected PromptGeneratorPort when no custom prompt is given."""
    mock_prompt = MagicMock()
    mock_generator = MagicMock(spec=PromptGeneratorPort)
    mock_generator.generate_cv_analysis_prompt.return_value = mock_prompt

    mock_structured_llm = MagicMock()
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm
    mock_chat_ollama.return_value = mock_llm_instance

    adapter = OllamaCVEvaluationChainAdapter(prompt_generator=mock_generator)
    adapter.create_chain()

    mock_generator.generate_cv_analysis_prompt.assert_called_once()


@patch("cv_analyzer.adapters.outbound.llm.ollama_chain_adapter.ChatOllama")
def test_create_chain_uses_custom_prompt_template(
    mock_chat_ollama: MagicMock,
) -> None:
    """Test that create_chain uses the provided prompt_template instead of the generator."""
    mock_generator = MagicMock(spec=PromptGeneratorPort)

    mock_structured_llm = MagicMock()
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm
    mock_chat_ollama.return_value = mock_llm_instance

    custom_prompt = MagicMock()
    adapter = OllamaCVEvaluationChainAdapter(prompt_generator=mock_generator)
    adapter.create_chain(prompt_template=custom_prompt)

    mock_generator.generate_cv_analysis_prompt.assert_not_called()


@patch("cv_analyzer.adapters.outbound.llm.ollama_chain_adapter.ChatOllama")
def test_create_chain_calls_chat_ollama_and_binds_output(
    mock_chat_ollama: MagicMock,
) -> None:
    """Test that ChatOllama is instantiated with expected parameters and structured output."""
    mock_structured_llm = MagicMock()
    mock_llm_instance = MagicMock()
    mock_llm_instance.with_structured_output.return_value = mock_structured_llm
    mock_chat_ollama.return_value = mock_llm_instance

    mock_generator = MagicMock(spec=PromptGeneratorPort)
    mock_generator.generate_cv_analysis_prompt.return_value = MagicMock()

    adapter = OllamaCVEvaluationChainAdapter(
        prompt_generator=mock_generator,
        model_name="qwen2.5:3b",
        base_url="http://ollama:11434",
        keep_alive="-1",
        timeout=45.0,
    )
    adapter.create_chain()

    mock_chat_ollama.assert_called_once_with(
        model="qwen2.5:3b",
        base_url="http://ollama:11434",
        temperature=0.2,
        repeat_penalty=1.15,
        keep_alive=-1,
        num_predict=900,
        num_ctx=4096,
        timeout=45.0,
    )
    mock_llm_instance.with_structured_output.assert_called_once_with(CVAnalysisResult)
