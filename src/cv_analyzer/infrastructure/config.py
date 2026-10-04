from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


def _load_env_file() -> None:
    """Load .env file from the workspace root into os.environ.

    Attempts to use python-dotenv if installed; otherwise falls back to a
    minimal standard library parser to avoid hard dependency failures.
    """
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if not env_path.exists():
        return

    try:
        from dotenv import load_dotenv

        load_dotenv(dotenv_path=env_path)
    except ImportError:
        # Fallback stdlib parser when python-dotenv is not yet installed
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                stripped = line.strip()
                if not stripped or stripped.startswith("#") or "=" not in stripped:
                    continue
                key, val = stripped.split("=", 1)
                key = key.strip()
                val = val.strip().strip("'\"")
                if key and key not in os.environ:
                    os.environ[key] = val


_load_env_file()


def _get_bool(key: str, default: bool = False) -> bool:
    """Helper to parse boolean values from environment variables."""
    val = os.getenv(key)
    if val is None:
        return default
    return val.strip().lower() in ("true", "1", "t", "yes", "y")


def _get_float(key: str, default: float) -> float:
    """Helper to parse float values from environment variables."""
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return float(val.strip())
    except ValueError:
        return default


@dataclass(frozen=True)
class LLMSettings:
    """Central configuration for LLM providers and resilience parameters."""

    # Google Gemini (Primary Provider)
    enable_gemini: bool = _get_bool("ENABLE_GEMINI", default=False)
    gemini_api_key: str | None = os.getenv("GEMINI_API_KEY") or None
    gemini_model_name: str = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")

    # OpenAI (Disabled by default to protect paid credits)
    enable_openai: bool = _get_bool("ENABLE_OPENAI", default=False)
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY") or None
    openai_model_name: str = os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini")
    openai_temperature: float = _get_float("OPENAI_TEMPERATURE", 0.2)

    # Future Providers (Prepared for subsequent fallback stages)
    enable_groq: bool = _get_bool("ENABLE_GROQ", default=False)
    groq_api_key: str | None = os.getenv("GROQ_API_KEY") or None
    groq_model_name: str = os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile")

    enable_openrouter: bool = _get_bool("ENABLE_OPENROUTER", default=False)
    openrouter_api_key: str | None = os.getenv("OPENROUTER_API_KEY") or None
    openrouter_model_name: str = os.getenv(
        "OPENROUTER_MODEL_NAME", "meta-llama/llama-3.3-70b-instruct:free"
    )

    enable_mistral: bool = _get_bool("ENABLE_MISTRAL", default=False)
    mistral_api_key: str | None = os.getenv("MISTRAL_API_KEY") or None
    mistral_model_name: str = os.getenv(
        "MISTRAL_MODEL_NAME", "mistral-small-latest"
    )

    # Resilience Settings
    timeout_seconds: float = _get_float("LLM_TIMEOUT_SECONDS", 15.0)


def get_llm_settings() -> LLMSettings:
    """Return the global LLMSettings instance."""
    return LLMSettings()
