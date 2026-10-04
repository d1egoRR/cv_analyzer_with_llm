"""Outbound LLM adapters package."""

from cv_analyzer.adapters.outbound.llm.exceptions import (
    AllProvidersExhaustedError,
    LLMProviderError,
)
from cv_analyzer.adapters.outbound.llm.fallback_chain_adapter import (
    FallbackCVEvaluationChainAdapter,
)
from cv_analyzer.adapters.outbound.llm.gemini_chain_adapter import (
    GeminiCVEvaluationChainAdapter,
)
from cv_analyzer.adapters.outbound.llm.openai_chain_adapter import (
    OpenAICVEvaluationChainAdapter,
)

__all__ = [
    "AllProvidersExhaustedError",
    "FallbackCVEvaluationChainAdapter",
    "GeminiCVEvaluationChainAdapter",
    "LLMProviderError",
    "OpenAICVEvaluationChainAdapter",
]
