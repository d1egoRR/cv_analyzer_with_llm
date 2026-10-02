from unittest.mock import MagicMock

from cv_analyzer.application.ports.prompt_generator import (
    PromptGeneratorPort,
)
from cv_analyzer.application.services.prompt_service import (
    PromptService,
)


def test_create_cv_analysis_prompt_delegates_to_generator() -> None:
    """Test that PromptService.create_cv_analysis_prompt delegates to PromptGeneratorPort."""
    expected_prompt = MagicMock()
    mock_generator = MagicMock(spec=PromptGeneratorPort)
    mock_generator.generate_cv_analysis_prompt.return_value = expected_prompt

    service = PromptService(generator=mock_generator)
    result = service.create_cv_analysis_prompt()

    mock_generator.generate_cv_analysis_prompt.assert_called_once_with(
        system_template=None,
        human_template=None,
    )

    assert result == expected_prompt


def test_create_cv_analysis_prompt_passes_custom_templates() -> None:
    """Test that custom templates are passed through to the generator."""
    expected_prompt = MagicMock()
    mock_generator = MagicMock(spec=PromptGeneratorPort)
    mock_generator.generate_cv_analysis_prompt.return_value = expected_prompt

    service = PromptService(generator=mock_generator)

    sys_tmpl = "Custom system template"
    hum_tmpl = "Custom human template"

    result = service.create_cv_analysis_prompt(
        system_template=sys_tmpl,
        human_template=hum_tmpl,
    )

    mock_generator.generate_cv_analysis_prompt.assert_called_once_with(
        system_template=sys_tmpl,
        human_template=hum_tmpl,
    )
    assert result == expected_prompt
