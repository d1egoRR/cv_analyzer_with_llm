from __future__ import annotations

from typing import Any, Protocol


class CVEvaluationChainPort(Protocol):
    """Port interface for creating CV evaluation LCEL chains."""

    provider_name: str
    model_name: str

    def create_chain(self, prompt_template: Any | None = None) -> Any:
        """Construct and return the LCEL evaluation chain (Runnable).

        Args:
            prompt_template: Optional prompt template to override default prompt.

        Returns:
            Constructed Runnable chain.
        """
        ...
