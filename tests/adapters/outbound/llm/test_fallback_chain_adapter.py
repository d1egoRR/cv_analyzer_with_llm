from unittest.mock import MagicMock

import pytest

from cv_analyzer.adapters.outbound.llm.exceptions import (
    AllProvidersExhaustedError,
    LLMProviderError,
)
from cv_analyzer.adapters.outbound.llm.fallback_chain_adapter import (
    FallbackCVEvaluationChainAdapter,
)
from cv_analyzer.application.ports.cv_evaluation_chain import (
    CVEvaluationChainPort,
)
from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult


def _create_sample_result(provider: str = "", model: str = "") -> CVAnalysisResult:
    return CVAnalysisResult(
        candidate_name="Alice Smith",
        years_of_experience=4.0,
        key_skills=["Python", "FastAPI"],
        education="B.S. Software Engineering",
        relevant_experience="Backend developer for 4 years",
        strengths=["FastAPI", "Clean Code"],
        areas_for_improvement=["Cloud infrastructure"],
        match_percentage=85,
        match_justification="Candidate matches backend requirements.",
        provider=provider,
        model=model,
    )


def test_fallback_succeeds_on_first_provider() -> None:
    """Test that primary provider is used when it succeeds, without calling secondary."""
    sample_result = _create_sample_result()

    mock_chain_1 = MagicMock()
    mock_chain_1.invoke.return_value = sample_result
    mock_adapter_1 = MagicMock(spec=CVEvaluationChainPort)
    mock_adapter_1.provider_name = "gemini"
    mock_adapter_1.model_name = "gemini-3.8-flash"
    mock_adapter_1.create_chain.return_value = mock_chain_1

    mock_chain_2 = MagicMock()
    mock_adapter_2 = MagicMock(spec=CVEvaluationChainPort)
    mock_adapter_2.provider_name = "openai"
    mock_adapter_2.model_name = "gpt-4o-mini"
    mock_adapter_2.create_chain.return_value = mock_chain_2

    fallback_adapter = FallbackCVEvaluationChainAdapter(
        providers=(
            ("gemini", mock_adapter_1),
            ("openai", mock_adapter_2),
        )
    )

    runner = fallback_adapter.create_chain()
    result = runner.invoke(
        {
            "job_description": "Job desc",
            "cv_text": "CV text",
        }
    )

    assert result.candidate_name == sample_result.candidate_name
    assert result.provider == "gemini"
    assert result.model == "gemini-3.8-flash"

    mock_adapter_1.create_chain.assert_called_once()
    mock_chain_1.invoke.assert_called_once()

    # Not called
    mock_adapter_2.create_chain.assert_not_called()
    mock_chain_2.invoke.assert_not_called()


def test_fallback_switches_to_second_provider_when_first_fails() -> None:
    """Test that when primary provider fails, the runner immediately switches to secondary."""
    sample_result = _create_sample_result()

    mock_chain_1 = MagicMock()
    mock_chain_1.invoke.side_effect = LLMProviderError("gemini", "Rate limit 429")
    mock_adapter_1 = MagicMock(spec=CVEvaluationChainPort)
    mock_adapter_1.provider_name = "gemini"
    mock_adapter_1.model_name = "gemini-3.8-flash"
    mock_adapter_1.create_chain.return_value = mock_chain_1

    mock_chain_2 = MagicMock()
    mock_chain_2.invoke.return_value = sample_result
    mock_adapter_2 = MagicMock(spec=CVEvaluationChainPort)
    mock_adapter_2.provider_name = "openai"
    mock_adapter_2.model_name = "gpt-4o-mini"
    mock_adapter_2.create_chain.return_value = mock_chain_2

    fallback_adapter = FallbackCVEvaluationChainAdapter(
        providers=(
            ("gemini", mock_adapter_1),
            ("openai", mock_adapter_2),
        )
    )

    runner = fallback_adapter.create_chain()
    result = runner.invoke({
        "job_description": "Job desc",
        "cv_text": "CV text",
    })

    assert result.candidate_name == sample_result.candidate_name
    assert result.provider == "openai"
    assert result.model == "gpt-4o-mini"

    mock_chain_1.invoke.assert_called_once()
    mock_chain_2.invoke.assert_called_once()


def test_fallback_exhausts_all_providers_raises_error() -> None:
    """Test that when all providers fail, AllProvidersExhaustedError is raised."""
    mock_chain_1 = MagicMock()
    mock_chain_1.invoke.side_effect = RuntimeError("Gemini 503 Outage")
    mock_adapter_1 = MagicMock(spec=CVEvaluationChainPort)
    mock_adapter_1.create_chain.return_value = mock_chain_1

    mock_chain_2 = MagicMock()
    mock_chain_2.invoke.side_effect = RuntimeError("OpenAI 429 Limit")
    mock_adapter_2 = MagicMock(spec=CVEvaluationChainPort)
    mock_adapter_2.create_chain.return_value = mock_chain_2

    fallback_adapter = FallbackCVEvaluationChainAdapter(
        providers=(
            ("gemini", mock_adapter_1),
            ("openai", mock_adapter_2),
        )
    )

    runner = fallback_adapter.create_chain()

    with pytest.raises(AllProvidersExhaustedError) as exc_info:
        runner.invoke(
            {
                "job_description": "Job desc",
                "cv_text": "CV text",
            }
        )

    assert len(exc_info.value.errors) == 2
    assert "Gemini 503 Outage" in str(exc_info.value.errors[0])
    assert "OpenAI 429 Limit" in str(exc_info.value.errors[1])


def test_fallback_empty_providers_raises_error() -> None:
    """Test that configuring no providers immediately raises AllProvidersExhaustedError."""
    fallback_adapter = FallbackCVEvaluationChainAdapter(providers=[])
    runner = fallback_adapter.create_chain()

    with pytest.raises(AllProvidersExhaustedError) as exc_info:
        runner.invoke(
            {
                "job_description": "Job desc",
                "cv_text": "CV text",
            }
        )

    assert "No active LLM providers" in str(exc_info.value)


def test_fallback_is_stateless_across_calls() -> None:
    """Test that fallback does not block or suppress providers on subsequent calls."""
    sample_result = _create_sample_result()

    mock_chain_1 = MagicMock()
    # Call 1 fails on provider 1; Call 2 succeeds on provider 1
    mock_chain_1.invoke.side_effect = [
        RuntimeError("Temporary glitch"),
        sample_result,
    ]
    mock_adapter_1 = MagicMock(spec=CVEvaluationChainPort)
    mock_adapter_1.provider_name = "gemini"
    mock_adapter_1.model_name = "gemini-3.8-flash"
    mock_adapter_1.create_chain.return_value = mock_chain_1

    mock_chain_2 = MagicMock()
    mock_chain_2.invoke.return_value = sample_result
    mock_adapter_2 = MagicMock(spec=CVEvaluationChainPort)
    mock_adapter_2.provider_name = "openai"
    mock_adapter_2.model_name = "gpt-4o-mini"
    mock_adapter_2.create_chain.return_value = mock_chain_2

    fallback_adapter = FallbackCVEvaluationChainAdapter(
        providers=(
            ("gemini", mock_adapter_1),
            ("openai", mock_adapter_2),
        )
    )

    # First invocation: provider 1 fails, falls back to provider 2
    res1 = fallback_adapter.create_chain().invoke(
        {
            "job_description": "Job desc",
            "cv_text": "CV text",
        }
    )
    assert res1.candidate_name == sample_result.candidate_name
    assert res1.provider == "openai"
    assert res1.model == "gpt-4o-mini"
    mock_chain_1.invoke.assert_called_once()
    mock_chain_2.invoke.assert_called_once()

    # Second invocation: provider 1 is attempted fresh and succeeds
    res2 = fallback_adapter.create_chain().invoke(
        {
            "job_description": "Job desc",
            "cv_text": "CV text",
        }
    )
    assert res2.candidate_name == sample_result.candidate_name
    assert res2.provider == "gemini"
    assert res2.model == "gemini-3.8-flash"
    assert mock_chain_1.invoke.call_count == 2
    # mock_chain_2 was NOT called on second invocation
    assert mock_chain_2.invoke.call_count == 1
