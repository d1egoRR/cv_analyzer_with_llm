from __future__ import annotations

import logging
from typing import Any

from cv_analyzer.adapters.outbound.llm.exceptions import (
    AllProvidersExhaustedError,
    LLMProviderError,
)
from cv_analyzer.application.ports.cv_evaluation_chain import (
    CVEvaluationChainPort,
)
from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult

logger = logging.getLogger(__name__)


class _FallbackChainRunner:
    """Orchestrates stateless sequential failover across providers."""

    def __init__(
        self,
        providers: list[tuple[str, CVEvaluationChainPort]],
        prompt_template: Any | None = None,
    ) -> None:
        self._providers = providers
        self._prompt_template = prompt_template

    def invoke(
        self, input_data: dict[str, Any], config: Any = None
    ) -> CVAnalysisResult:
        """Execute evaluation by attempting providers sequentially.

        In each evaluation call, all configured providers are attempted in order.
        If a provider succeeds, its result is returned immediately.
        If a provider fails, the runner immediately proceeds to the next provider.

        Args:
            input_data: Dictionary containing 'job_description' and 'cv_text'.
            config: Optional LangChain configuration.

        Returns:
            Validated CVAnalysisResult from the first provider that succeeds.

        Raises:
            AllProvidersExhaustedError: If all configured providers fail.
        """
        if not self._providers:
            raise AllProvidersExhaustedError(
                [Exception("No active LLM providers are configured or enabled.")]
            )

        errors: list[Exception] = []

        for provider_id, adapter in self._providers:
            logger.info(
                f"Attempting CV evaluation with provider '{provider_id}'"
            )
            try:
                chain = adapter.create_chain(
                    prompt_template=self._prompt_template
                )
                result: CVAnalysisResult = chain.invoke(
                    input_data, config=config
                )
                logger.info(
                    f"CV evaluation succeeded using provider '{provider_id}'"
                )
                return result
            except Exception as exc:
                provider_err = (
                    exc
                    if isinstance(exc, LLMProviderError)
                    else LLMProviderError(provider_id, str(exc))
                )
                logger.warning(
                    f"Provider '{provider_id}' failed: {provider_err}. Falling back to next provider..."
                )
                errors.append(provider_err)

        raise AllProvidersExhaustedError(errors)


class FallbackCVEvaluationChainAdapter(CVEvaluationChainPort):
    """Composite outbound adapter managing stateless multi-provider fallback."""

    def __init__(
        self,
        providers: list[tuple[str, CVEvaluationChainPort]],
    ) -> None:
        """Initialize FallbackCVEvaluationChainAdapter.

        Args:
            providers: Ordered list of (provider_id, adapter) tuples.
        """
        self._providers = providers

    def create_chain(self, prompt_template: Any | None = None) -> Any:
        """Create and return a composite fallback runner.

        Args:
            prompt_template: Optional prompt template override.

        Returns:
            A runnable object providing an .invoke() method with fallback logic.
        """
        return _FallbackChainRunner(
            providers=self._providers,
            prompt_template=prompt_template,
        )
