from unittest.mock import MagicMock, patch

from cv_analyzer.adapters.outbound.llm.openai_chain_adapter import (
    OpenAICVEvaluationChainAdapter,
)
from cv_analyzer.application.ports.prompt_generator import (
    PromptGeneratorPort,
)


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

    adapter = OpenAICVEvaluationChainAdapter(prompt_generator=mock_generator)
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
    adapter = OpenAICVEvaluationChainAdapter(prompt_generator=mock_generator)
    adapter.create_chain(prompt_template=custom_prompt)

    mock_generator.generate_cv_analysis_prompt.assert_not_called()


@patch("cv_analyzer.adapters.outbound.llm.openai_chain_adapter.ChatOpenAI")
def test_create_chain_calls_with_structured_output(mock_chat_openai: MagicMock) -> None:
    """Test that create_chain calls with_structured_output with CVAnalysisResult."""
    from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult

    mock_generator = MagicMock(spec=PromptGeneratorPort)
    mock_generator.generate_cv_analysis_prompt.return_value = MagicMock()

    mock_llm_instance = MagicMock()
    mock_chat_openai.return_value = mock_llm_instance

    adapter = OpenAICVEvaluationChainAdapter(prompt_generator=mock_generator)
    adapter.create_chain()

    mock_llm_instance.with_structured_output.assert_called_once_with(CVAnalysisResult)
