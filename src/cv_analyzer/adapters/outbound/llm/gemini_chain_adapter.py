from __future__ import annotations

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI

from cv_analyzer.adapters.outbound.llm.exceptions import LLMProviderError
from cv_analyzer.application.ports.cv_evaluation_chain import (
    CVEvaluationChainPort,
)
from cv_analyzer.application.ports.prompt_generator import (
    PromptGeneratorPort,
)
from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult
from cv_analyzer.infrastructure.config import get_llm_settings


class GeminiCVEvaluationChainAdapter(CVEvaluationChainPort):
    """Outbound adapter responsible for creating LCEL chains using Google Gemini."""

    PROVIDER_NAME = "gemini"

    def __init__(
        self,
        prompt_generator: PromptGeneratorPort,
        model_name: str | None = None,
        api_key: str | None = None,
        timeout: float | None = None,
    ) -> None:
        """Initialize GeminiCVEvaluationChainAdapter.

        Args:
            prompt_generator: Injected port for generating prompt templates.
            model_name: Optional override for Gemini model.
            api_key: Optional override for Google Gemini API key.
            timeout: Optional request timeout in seconds.
        """
        settings = get_llm_settings()
        self._prompt_generator = prompt_generator
        self._model_name = model_name or settings.gemini_model_name
        self._api_key = (
            settings.gemini_api_key if api_key is None else api_key
        )
        self._timeout = timeout or settings.timeout_seconds

    @property
    def provider_name(self) -> str:
        """Return the provider identifier."""
        return self.PROVIDER_NAME

    @property
    def model_name(self) -> str:
        """Return the configured model name."""
        return self._model_name

    def create_chain(
        self,
        prompt_template: ChatPromptTemplate | None = None,
    ) -> Any:
        """Construct ChatGoogleGenerativeAI, bind structured output, and return LCEL chain.

        Args:
            prompt_template: Optional custom ChatPromptTemplate.
                If None, uses the injected PromptGeneratorPort.

        Returns:
            Constructed Runnable chain returning CVAnalysisResult.

        Raises:
            LLMProviderError: If credentials, dependencies, or parameters fail.
        """
        if not self._api_key or not self._api_key.strip():
            raise LLMProviderError(
                self.PROVIDER_NAME,
                "GEMINI_API_KEY is not configured. Please set it in .env.",
            )

        prompt = (
            prompt_template
            or self._prompt_generator.generate_cv_analysis_prompt()
        )

        llm = ChatGoogleGenerativeAI(
            model=self._model_name,
            google_api_key=self._api_key,
            temperature=0.0,
            timeout=self._timeout,
            max_retries=0,
        )

        structured_llm = llm.with_structured_output(CVAnalysisResult)
        return prompt | structured_llm
