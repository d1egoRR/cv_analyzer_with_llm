from __future__ import annotations

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from cv_analyzer.adapters.outbound.llm.exceptions import LLMProviderError
from cv_analyzer.application.ports.cv_evaluation_chain import (
    CVEvaluationChainPort,
)
from cv_analyzer.application.ports.prompt_generator import (
    PromptGeneratorPort,
)
from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult
from cv_analyzer.infrastructure.config import get_llm_settings


class OpenAICVEvaluationChainAdapter(CVEvaluationChainPort):
    """Outbound adapter responsible for creating LCEL chains using ChatOpenAI or compatible endpoints."""

    def __init__(
        self,
        prompt_generator: PromptGeneratorPort,
        model_name: str | None = None,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        provider_name: str = "openai",
    ) -> None:
        """Initialize OpenAICVEvaluationChainAdapter.

        Args:
            prompt_generator: Injected port for generating prompt templates.
            model_name: Model identifier (e.g. 'gpt-4o-mini', 'llama-3.3-70b-versatile').
            api_key: API key for the endpoint.
            base_url: Optional custom base URL for OpenAI-compatible providers.
            timeout: Optional request timeout in seconds.
            provider_name: Identifier for error reporting and cooldown tracking.
        """
        settings = get_llm_settings()
        self._prompt_generator = prompt_generator
        self._provider_name = provider_name
        self._model_name = model_name or settings.openai_model_name
        self._api_key = (
            settings.openai_api_key if api_key is None else api_key
        )
        self._base_url = base_url
        self._temperature = settings.openai_temperature
        self._timeout = timeout or settings.timeout_seconds

    def create_chain(
        self,
        prompt_template: ChatPromptTemplate | None = None,
    ) -> Any:
        """Construct ChatOpenAI, bind structured output, and return LCEL chain.

        Args:
            prompt_template: Optional custom ChatPromptTemplate.
                If None, uses the injected PromptGeneratorPort.

        Returns:
            Constructed Runnable chain returning CVAnalysisResult.

        Raises:
            LLMProviderError: If API key is not configured.
        """
        if not self._api_key or not self._api_key.strip():
            raise LLMProviderError(
                self._provider_name,
                f"API key for provider '{self._provider_name}' is not configured.",
            )

        prompt = (
            prompt_template
            or self._prompt_generator.generate_cv_analysis_prompt()
        )

        llm_kwargs: dict[str, Any] = {
            "model": self._model_name,
            "temperature": self._temperature,
            "api_key": self._api_key,
            "timeout": self._timeout,
            "max_retries": 0,
        }
        if self._base_url:
            llm_kwargs["base_url"] = self._base_url

        llm = ChatOpenAI(**llm_kwargs)
        structured_llm = llm.with_structured_output(CVAnalysisResult)
        return prompt | structured_llm
