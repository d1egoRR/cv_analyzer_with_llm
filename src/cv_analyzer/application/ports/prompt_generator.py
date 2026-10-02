from __future__ import annotations

from typing import Any, Protocol


class PromptGeneratorPort(Protocol):
    """Port interface defining prompt template generation capabilities."""

    def generate_cv_analysis_prompt(
        self,
        system_template: str | None = None,
        human_template: str | None = None,
    ) -> Any:
        """Generate a chat prompt template containing system and human message prompts.

        Args:
            system_template: Optional system prompt template string.
            human_template: Optional human prompt template string.

        Returns:
            Constructed prompt template object.
        """
        ...
