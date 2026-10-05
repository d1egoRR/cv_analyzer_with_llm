from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


def _load_env_file() -> None:
    """Load .env file from the workspace root into os.environ.

    Skips loading if running in a test environment (e.g. under pytest).
    """
    if (
        "PYTEST_CURRENT_TEST" in os.environ
        or os.getenv("TESTING", "").lower() in ("true", "1")
    ):
        return

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


def _get_int(key: str, default: int) -> int:
    """Helper to parse integer values from environment variables."""
    val = os.getenv(key)
    if val is None:
        return default
    try:
        return int(val.strip())
    except ValueError:
        return default


@dataclass(frozen=True)
class LLMSettings:
    """Central configuration for LLM providers and resilience parameters."""

    enable_gemini: bool = False
    gemini_api_key: str | None = None
    gemini_model_name: str = "gemini-1.5-flash"

    enable_openai: bool = False
    openai_api_key: str | None = None
    openai_model_name: str = "gpt-4o-mini"
    openai_temperature: float = 0.2

    enable_groq: bool = False
    groq_api_key: str | None = None
    groq_model_name: str = "llama-3.3-70b-versatile"

    enable_openrouter: bool = False
    openrouter_api_key: str | None = None
    openrouter_model_name: str = "meta-llama/llama-3.3-70b-instruct:free"

    enable_mistral: bool = False
    mistral_api_key: str | None = None
    mistral_model_name: str = "mistral-small-latest"

    enable_ollama: bool = False
    ollama_base_url: str = "http://localhost:11434"
    ollama_model_name: str = "qwen2.5:3b"
    ollama_keep_alive: str = "-1"
    ollama_timeout_seconds: float = 300.0
    ollama_num_predict: int = 900
    ollama_num_ctx: int = 4096

    timeout_seconds: float = 15.0

    @classmethod
    def from_env(cls) -> LLMSettings:
        """Create an LLMSettings instance dynamically from current environment variables."""
        return cls(
            enable_gemini=_get_bool("ENABLE_GEMINI", default=False),
            gemini_api_key=os.getenv("GEMINI_API_KEY") or None,
            gemini_model_name=os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash"),
            enable_openai=_get_bool("ENABLE_OPENAI", default=False),
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_model_name=os.getenv("OPENAI_MODEL_NAME", "gpt-4o-mini"),
            openai_temperature=_get_float("OPENAI_TEMPERATURE", 0.2),
            enable_groq=_get_bool("ENABLE_GROQ", default=False),
            groq_api_key=os.getenv("GROQ_API_KEY") or None,
            groq_model_name=os.getenv("GROQ_MODEL_NAME", "llama-3.3-70b-versatile"),
            enable_openrouter=_get_bool("ENABLE_OPENROUTER", default=False),
            openrouter_api_key=os.getenv("OPENROUTER_API_KEY") or None,
            openrouter_model_name=os.getenv(
                "OPENROUTER_MODEL_NAME", "meta-llama/llama-3.3-70b-instruct:free"
            ),
            enable_mistral=_get_bool("ENABLE_MISTRAL", default=False),
            mistral_api_key=os.getenv("MISTRAL_API_KEY") or None,
            mistral_model_name=os.getenv(
                "MISTRAL_MODEL_NAME", "mistral-small-latest"
            ),
            enable_ollama=_get_bool("ENABLE_OLLAMA", default=False),
            ollama_base_url=os.getenv(
                "OLLAMA_BASE_URL", "http://localhost:11434"
            ),
            ollama_model_name=os.getenv("OLLAMA_MODEL_NAME", "qwen2.5:3b"),
            ollama_keep_alive=os.getenv("OLLAMA_KEEP_ALIVE", "-1"),
            ollama_timeout_seconds=_get_float(
                "OLLAMA_TIMEOUT_SECONDS", 300.0
            ),
            ollama_num_predict=_get_int("OLLAMA_NUM_PREDICT", 900),
            ollama_num_ctx=_get_int("OLLAMA_NUM_CTX", 4096),
            timeout_seconds=_get_float("LLM_TIMEOUT_SECONDS", 15.0),
        )


def get_llm_settings() -> LLMSettings:
    """Return the current LLMSettings instance dynamically from environment."""
    return LLMSettings.from_env()
