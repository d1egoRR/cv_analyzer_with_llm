from __future__ import annotations

import os
from typing import Any

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from cv_analyzer.application.ports.cv_evaluation_chain import (
    CVEvaluationChainPort,
)
from cv_analyzer.application.ports.prompt_generator import (
    PromptGeneratorPort,
)
from cv_analyzer.domain.models.cv_analysis_result import CVAnalysisResult


class OpenAICVEvaluationChainAdapter(CVEvaluationChainPort):
    """Outbound adapter responsible for creating LCEL chains using ChatOpenAI."""

    DEFAULT_MODEL_NAME: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    DEFAULT_TEMPERATURE: float = float(os.getenv("OPENAI_TEMPERATURE", "0.0"))

    def __init__(self, prompt_generator: PromptGeneratorPort) -> None:
        """Initialize OpenAICVEvaluationChainAdapter.

        Args:
            prompt_generator: Injected port for generating prompt templates.
        """
        self._prompt_generator = prompt_generator

    def create_chain(
        self,
        prompt_template: ChatPromptTemplate | None = None,
    ) -> Any:
        """Construct ChatOpenAI, bind structured output, and return LCEL chain.

        Args:
            prompt_template: Optional custom ChatPromptTemplate.
                If None, uses the injected PromptGeneratorPort.

        Returns:
            Runnable LCEL chain (prompt | structured_llm).
        """
        prompt = prompt_template or self._prompt_generator.generate_cv_analysis_prompt()

        llm = ChatOpenAI(
            model=self.DEFAULT_MODEL_NAME,
            temperature=self.DEFAULT_TEMPERATURE,
            api_key=os.getenv("OPENAI_API_KEY"),
        )
        structured_llm = llm.with_structured_output(CVAnalysisResult)

        return prompt | structured_llm
