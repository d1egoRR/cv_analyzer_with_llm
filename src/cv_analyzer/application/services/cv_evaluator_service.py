from __future__ import annotations

from cv_analyzer.application.ports.cv_evaluation_chain import (
    CVEvaluationChainPort,
)
from cv_analyzer.domain.exceptions import CVEvaluationError
from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult


class CVEvaluatorService:
    """Application service for executing CV evaluations using a chain provider."""

    def __init__(self, chain_provider: CVEvaluationChainPort) -> None:
        """Initialize CVEvaluatorService.

        Args:
            chain_provider: Outbound adapter creating LCEL evaluation chains.
        """
        self._chain_provider = chain_provider

    def evaluate(self, job_description: str, cv_text: str) -> CVAnalysisResult:
        """Evaluate CV text against job description by invoking the LCEL chain.

        Args:
            job_description: Target job requirements text string.
            cv_text: Candidate CV text string (already extracted).

        Returns:
            CVAnalysisResult containing structured evaluation metrics.

        Raises:
            CVEvaluationError: If chain creation or invocation fails.
        """
        try:
            chain = self._chain_provider.create_chain()
            result: CVAnalysisResult = chain.invoke(
                {
                    "job_description": job_description,
                    "cv_text": cv_text,
                }
            )
        except Exception as exc:
            raise CVEvaluationError(
                f"Failed to evaluate CV: {exc}"
            ) from exc

        return result

