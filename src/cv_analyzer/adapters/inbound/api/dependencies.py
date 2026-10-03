from functools import lru_cache

from cv_analyzer.adapters.outbound.llm.openai_chain_adapter import (
    OpenAICVEvaluationChainAdapter,
)
from cv_analyzer.adapters.outbound.pdf.pypdf_extractor import PyPDFExtractor
from cv_analyzer.adapters.outbound.prompts.langchain_prompt_adapter import (
    LangChainPromptAdapter,
)
from cv_analyzer.application.services.cv_evaluator_service import (
    CVEvaluatorService,
)
from cv_analyzer.application.services.pdf_service import PDFService
from cv_analyzer.application.services.prompt_service import PromptService


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
    """Provide a configured CVEvaluatorService with OpenAICVEvaluationChainAdapter.

    Returns:
        Configured CVEvaluatorService instance.
    """
    prompt_generator = LangChainPromptAdapter()
    chain_adapter = OpenAICVEvaluationChainAdapter(
        prompt_generator=prompt_generator
    )
    return CVEvaluatorService(chain_provider=chain_adapter)
