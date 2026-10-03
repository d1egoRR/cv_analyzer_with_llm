from unittest.mock import MagicMock

import pytest

from cv_analyzer.application.ports.cv_evaluation_chain import (
    CVEvaluationChainPort,
)
from cv_analyzer.application.services.cv_evaluator_service import (
    CVEvaluatorService,
)
from cv_analyzer.domain.exceptions import CVEvaluationError
from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult


def test_evaluate_delegates_to_chain_provider() -> None:
    """Test that evaluate creates a chain and invokes it with the correct arguments."""
    expected_result = MagicMock(spec=CVAnalysisResult)
    mock_chain = MagicMock()
    mock_chain.invoke.return_value = expected_result

    mock_chain_provider = MagicMock(spec=CVEvaluationChainPort)
    mock_chain_provider.create_chain.return_value = mock_chain

    service = CVEvaluatorService(chain_provider=mock_chain_provider)

    result = service.evaluate(
        job_description="Senior Python Developer",
        cv_text="5 years of Python experience",
    )

    mock_chain_provider.create_chain.assert_called_once()
    mock_chain.invoke.assert_called_once_with(
        {
            "descripcion_puesto": "Senior Python Developer",
            "texto_cv": "5 years of Python experience",
        }
    )
    assert result == expected_result


def test_evaluate_raises_cv_evaluation_error_on_chain_creation_failure() -> None:
    """Test that CVEvaluationError is raised when create_chain fails."""
    mock_chain_provider = MagicMock(spec=CVEvaluationChainPort)
    mock_chain_provider.create_chain.side_effect = RuntimeError("Connection failed")

    service = CVEvaluatorService(chain_provider=mock_chain_provider)

    with pytest.raises(CVEvaluationError, match="Failed to evaluate CV"):
        service.evaluate(
            job_description="Backend Developer",
            cv_text="Some CV text",
        )


def test_evaluate_raises_cv_evaluation_error_on_invoke_failure() -> None:
    """Test that CVEvaluationError is raised when chain.invoke fails."""
    mock_chain = MagicMock()
    mock_chain.invoke.side_effect = RuntimeError("API timeout")

    mock_chain_provider = MagicMock(spec=CVEvaluationChainPort)
    mock_chain_provider.create_chain.return_value = mock_chain

    service = CVEvaluatorService(chain_provider=mock_chain_provider)

    with pytest.raises(CVEvaluationError, match="Failed to evaluate CV") as exc_info:
        service.evaluate(
            job_description="Backend Developer",
            cv_text="Some CV text",
        )

    assert isinstance(exc_info.value.__cause__, RuntimeError)
