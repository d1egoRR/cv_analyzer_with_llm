from __future__ import annotations

from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from cv_analyzer.application.ports.cv_evaluation_chain import (
    CVEvaluationChainPort,
)
from cv_analyzer.application.ports.prompt_generator import (
    PromptGeneratorPort,
)
from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult
from cv_analyzer.infrastructure.config import get_llm_settings


def _parse_keep_alive(val: str | int | None) -> int | str | None:
    """Parse keep_alive value into an integer if numeric, or string with duration units."""
    if val is None:
        return None
    if isinstance(val, int):
        return val
    val_str = str(val).strip()
    if val_str.lstrip("-").isdigit():
        return int(val_str)
    return val_str


class OllamaCVEvaluationChainAdapter(CVEvaluationChainPort):
    """Outbound adapter responsible for creating LCEL chains using local Ollama."""

    PROVIDER_NAME = "ollama"

    def __init__(
        self,
        prompt_generator: PromptGeneratorPort,
        model_name: str | None = None,
        base_url: str | None = None,
        keep_alive: str | int | None = None,
        num_predict: int | None = None,
        repeat_penalty: float | None = None,
        num_ctx: int | None = None,
        timeout: float | None = None,
    ) -> None:
        """Initialize OllamaCVEvaluationChainAdapter.

        Args:
            prompt_generator: Injected port for generating prompt templates.
            model_name: Optional override for Ollama model (defaults to qwen2.5:3b).
            base_url: Optional override for Ollama server URL.
            keep_alive: Duration or flag to keep model resident in memory (defaults to -1).
            num_predict: Maximum tokens to generate (limits excessive output and ensures fast response).
            repeat_penalty: Repetition penalty factor to prevent degenerate token loops (defaults to 1.15).
            num_ctx: Context window size in tokens to prevent truncating long CVs (defaults to 4096).
            timeout: Optional request timeout in seconds.
        """
        settings = get_llm_settings()
        self._prompt_generator = prompt_generator
        self._model_name = model_name or settings.ollama_model_name
        self._base_url = base_url or settings.ollama_base_url
        self._keep_alive = _parse_keep_alive(
            keep_alive if keep_alive is not None else settings.ollama_keep_alive
        )
        self._num_predict = num_predict or settings.ollama_num_predict
        self._repeat_penalty = repeat_penalty or 1.15
        self._num_ctx = num_ctx or settings.ollama_num_ctx
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
        """Construct ChatOllama, bind structured output, and return LCEL chain.

        Args:
            prompt_template: Optional custom ChatPromptTemplate.
                If None, uses the injected PromptGeneratorPort.

        Returns:
            Constructed Runnable chain returning CVAnalysisResult.
        """
        prompt = (
            prompt_template
            or self._prompt_generator.generate_cv_analysis_prompt()
        )

        llm = ChatOllama(
            model=self._model_name,
            base_url=self._base_url,
            temperature=0.2,
            repeat_penalty=self._repeat_penalty,
            keep_alive=self._keep_alive,
            num_predict=self._num_predict,
            num_ctx=self._num_ctx,
            timeout=self._timeout,
        )

        structured_llm = llm.with_structured_output(CVAnalysisResult)
        return prompt | structured_llm
