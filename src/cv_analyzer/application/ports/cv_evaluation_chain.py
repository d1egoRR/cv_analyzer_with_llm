from __future__ import annotations

from typing import Any, Protocol


class CVEvaluationChainPort(Protocol):
    """Port interface for creating CV evaluation LCEL chains."""

    def create_chain(self) -> Any:
        """Construct and return the LCEL evaluation chain (Runnable).

        Returns:
            Constructed Runnable chain.
        """
        ...
