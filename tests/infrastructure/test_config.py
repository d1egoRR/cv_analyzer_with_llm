import os
from unittest.mock import patch

from cv_analyzer.infrastructure.config import (
    LLMSettings,
    _get_bool,
    _get_float,
    get_llm_settings,
)


def test_get_bool_truthy_values() -> None:
    """Test that _get_bool recognizes standard truthy representations."""
    for truthy in ("true", "TRUE", "1", "yes", "YES", "t", "y"):
        with patch.dict(os.environ, {"TEST_FLAG": truthy}):
            assert _get_bool("TEST_FLAG", default=False) is True


def test_get_bool_falsy_values() -> None:
    """Test that _get_bool recognizes falsy strings and defaults."""
    for falsy in ("false", "FALSE", "0", "no", "n"):
        with patch.dict(os.environ, {"TEST_FLAG": falsy}):
            assert _get_bool("TEST_FLAG", default=True) is False

    with patch.dict(os.environ, {}, clear=True):
        assert _get_bool("NON_EXISTENT_VAR", default=True) is True
        assert _get_bool("NON_EXISTENT_VAR", default=False) is False


def test_get_float_valid_and_invalid() -> None:
    """Test that _get_float parses numeric strings and falls back to default on error."""
    with patch.dict(os.environ, {"FLOAT_VAL": "12.5"}):
        assert _get_float("FLOAT_VAL", default=0.0) == 12.5

    with patch.dict(os.environ, {"FLOAT_VAL": "not-a-number"}):
        assert _get_float("FLOAT_VAL", default=10.0) == 10.0

    with patch.dict(os.environ, {}, clear=True):
        assert _get_float("MISSING_VAL", default=5.5) == 5.5


def test_llm_settings_models_and_flags() -> None:
    """Test LLMSettings instantiation and field values."""
    settings = get_llm_settings()
    assert isinstance(settings, LLMSettings)
    assert settings.gemini_model_name == "gemini-1.5-flash"
    assert settings.openai_model_name == "gpt-4o-mini"
    assert settings.ollama_model_name == "qwen2.5:3b"
    assert settings.ollama_keep_alive == "-1"
    assert settings.timeout_seconds == 15.0


def test_llm_settings_ollama_custom_env() -> None:
    """Test LLMSettings parses custom Ollama environment variables."""
    custom_env = {
        "ENABLE_OLLAMA": "true",
        "OLLAMA_BASE_URL": "http://ollama-custom:11434",
        "OLLAMA_MODEL_NAME": "qwen2.5:7b",
        "OLLAMA_KEEP_ALIVE": "24h",
    }
    with patch.dict(os.environ, custom_env):
        settings = get_llm_settings()
        assert settings.enable_ollama is True
        assert settings.ollama_base_url == "http://ollama-custom:11434"
        assert settings.ollama_model_name == "qwen2.5:7b"
        assert settings.ollama_keep_alive == "24h"

