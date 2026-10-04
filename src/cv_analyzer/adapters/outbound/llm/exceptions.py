from __future__ import annotations


class LLMProviderError(Exception):
    """Base exception for all outbound LLM adapter errors."""

    def __init__(self, provider: str, message: str) -> None:
        self.provider = provider
        self.message = message
        super().__init__(f"[{provider}] {message}")


class AllProvidersExhaustedError(Exception):
    """Raised when all configured LLM providers have failed or are in cooldown."""

    def __init__(self, errors: list[Exception]) -> None:
        self.errors = errors
        error_details = "; ".join(str(e) for e in errors)
        super().__init__(
            f"All LLM providers were exhausted or unavailable: {error_details}"
        )
