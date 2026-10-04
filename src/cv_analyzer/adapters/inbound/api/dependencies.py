from functools import lru_cache

from cv_analyzer.adapters.outbound.llm.fallback_chain_adapter import (
    FallbackCVEvaluationChainAdapter,
)
from cv_analyzer.adapters.outbound.llm.gemini_chain_adapter import (
    GeminiCVEvaluationChainAdapter,
)
from cv_analyzer.adapters.outbound.llm.openai_chain_adapter import (
    OpenAICVEvaluationChainAdapter,
)
from cv_analyzer.adapters.outbound.pdf.pypdf_extractor import PyPDFExtractor
from cv_analyzer.adapters.outbound.prompts.langchain_prompt_adapter import (
    LangChainPromptAdapter,
)
from cv_analyzer.application.ports.cv_evaluation_chain import (
    CVEvaluationChainPort,
)
from cv_analyzer.application.services.cv_evaluator_service import (
    CVEvaluatorService,
)
from cv_analyzer.application.services.pdf_service import PDFService
from cv_analyzer.application.services.prompt_service import PromptService
from cv_analyzer.infrastructure.config import get_llm_settings


@lru_cache
def get_pdf_service() -> PDFService:
    """Provide a configured PDFService instance with PyPDFExtractor adapter.

    Returns:
        Configured PDFService instance.
    """
    extractor = PyPDFExtractor()
    return PDFService(extractor=extractor)


@lru_cache
def get_prompt_service() -> PromptService:
    """Provide a configured PromptService instance with LangChainPromptAdapter.

    Returns:
        Configured PromptService instance.
    """
    generator = LangChainPromptAdapter()
    return PromptService(generator=generator)


@lru_cache
def get_cv_evaluator_service() -> CVEvaluatorService:
    """Provide a configured CVEvaluatorService with stateless FallbackCVEvaluationChainAdapter.

    Assembles enabled LLM providers based on environment configuration.

    Returns:
        Configured CVEvaluatorService instance.
    """
    settings = get_llm_settings()
    prompt_generator = LangChainPromptAdapter()
    providers: list[tuple[str, CVEvaluationChainPort]] = []

    if settings.enable_gemini:
        providers.append(
            (
                "gemini",
                GeminiCVEvaluationChainAdapter(
                    prompt_generator=prompt_generator,
                    model_name=settings.gemini_model_name,
                    api_key=settings.gemini_api_key,
                    timeout=settings.timeout_seconds,
                ),
            )
        )

    if settings.enable_openai:
        providers.append(
            (
                "openai",
                OpenAICVEvaluationChainAdapter(
                    prompt_generator=prompt_generator,
                    model_name=settings.openai_model_name,
                    api_key=settings.openai_api_key,
                    timeout=settings.timeout_seconds,
                    provider_name="openai",
                ),
            )
        )

    fallback_adapter = FallbackCVEvaluationChainAdapter(providers=providers)
    return CVEvaluatorService(chain_provider=fallback_adapter)
