from __future__ import annotations

from typing import Any

from cv_analyzer.application.ports.prompt_generator import PromptGeneratorPort


class PromptService:
    """Application service for orchestrating prompt generation operations."""

    def __init__(self, generator: PromptGeneratorPort) -> None:
        """Initialize PromptService with a PromptGeneratorPort implementation.

        Args:
            generator: Outbound adapter matching PromptGeneratorPort protocol.
        """
        self._generator = generator

    def create_cv_analysis_prompt(
        self,
        system_template: str | None = None,
        human_template: str | None = None,
    ) -> Any:
        """Create prompt template for CV analysis using the configured generator.

        Args:
            system_template: Optional custom system prompt string with placeholders.
            human_template: Optional custom human prompt string with placeholders.

        Returns:
            Constructed prompt template.
        """
        return self._generator.generate_cv_analysis_prompt(
            system_template=system_template,
            human_template=human_template,
        )
